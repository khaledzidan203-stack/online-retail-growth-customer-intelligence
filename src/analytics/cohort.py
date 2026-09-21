"""Build governed customer cohort, retention, and repeat-timing outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from validation import connect_sql, json_value, numeric, query_frame


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "outputs"
FIGURE_DIR = OUTPUT_DIR / "figures"
EXPECTED_CUSTOMERS = 5_852
EXPECTED_REVENUE = 17_125_672.047
EXPECTED_ORDERS = 36_597
CHECKPOINT_MONTHS = [1, 2, 3, 6, 12]


def load_orders(connection: Any) -> tuple[pd.DataFrame, dict[str, Any]]:
    orders = query_frame(
        connection,
        """
        SELECT
            customer.CustomerID,
            fact.Invoice,
            MIN(fact.InvoiceDate) AS PurchaseDate,
            SUM(fact.LineAmount) AS Revenue,
            SUM(CONVERT(BIGINT, fact.Quantity)) AS Units
        FROM analytics.FactTransaction AS fact
        INNER JOIN analytics.DimCustomer AS customer
            ON customer.CustomerKey = fact.CustomerKey
        WHERE fact.IsCustomerAnalyticsEligible = 1
        GROUP BY customer.CustomerID, fact.Invoice;
        """,
    )
    governed = query_frame(
        connection,
        """
        SELECT
            COUNT(DISTINCT CustomerKey) AS CustomerCount,
            COUNT(DISTINCT Invoice) AS OrderCount,
            SUM(LineAmount) AS Revenue,
            SUM(CONVERT(BIGINT, Quantity)) AS Units,
            MIN(InvoiceDate) AS MinimumInvoiceDate,
            MAX(InvoiceDate) AS MaximumInvoiceDate
        FROM analytics.FactTransaction
        WHERE IsCustomerAnalyticsEligible = 1;
        """,
    ).iloc[0]
    return orders, governed.to_dict()


def build_customer_timing(orders: pd.DataFrame) -> pd.DataFrame:
    ordered = orders.sort_values(["CustomerID", "PurchaseDate", "Invoice"]).copy()
    ordered["OrderSequence"] = ordered.groupby("CustomerID").cumcount() + 1
    first = ordered.loc[ordered["OrderSequence"].eq(1), ["CustomerID", "PurchaseDate"]]
    first = first.rename(columns={"PurchaseDate": "FirstPurchaseDate"})
    second = ordered.loc[ordered["OrderSequence"].eq(2), ["CustomerID", "PurchaseDate"]]
    second = second.rename(columns={"PurchaseDate": "SecondPurchaseDate"})
    customers = first.merge(second, on="CustomerID", how="left", validate="one_to_one")
    customers["AcquisitionCohort"] = customers["FirstPurchaseDate"].dt.to_period("M")
    customers["HasRepeatPurchase"] = customers["SecondPurchaseDate"].notna()
    customers["DaysToSecondPurchase"] = (
        customers["SecondPurchaseDate"].dt.normalize()
        - customers["FirstPurchaseDate"].dt.normalize()
    ).dt.days.astype("Int64")
    return customers


def build_cohort_cells(
    orders: pd.DataFrame,
    customers: pd.DataFrame,
    observation_month: pd.Period,
) -> pd.DataFrame:
    activity = orders.merge(
        customers[["CustomerID", "AcquisitionCohort"]],
        on="CustomerID",
        how="left",
        validate="many_to_one",
    )
    activity["ActivityMonth"] = activity["PurchaseDate"].dt.to_period("M")
    activity["CohortIndex"] = (
        (activity["ActivityMonth"].dt.year - activity["AcquisitionCohort"].dt.year) * 12
        + activity["ActivityMonth"].dt.month
        - activity["AcquisitionCohort"].dt.month
    )
    cohort_sizes = customers.groupby("AcquisitionCohort")["CustomerID"].nunique()
    observed = activity.groupby(
        ["AcquisitionCohort", "CohortIndex", "ActivityMonth"], observed=True
    ).agg(
        ActiveCustomers=("CustomerID", "nunique"),
        Revenue=("Revenue", "sum"),
        Orders=("Invoice", "nunique"),
    ).reset_index()

    grid_rows = []
    for cohort, cohort_size in cohort_sizes.items():
        maximum_index = int(observation_month.ordinal - cohort.ordinal)
        for index in range(maximum_index + 1):
            grid_rows.append(
                {
                    "AcquisitionCohort": cohort,
                    "CohortIndex": index,
                    "ActivityMonth": cohort + index,
                    "CohortSize": int(cohort_size),
                }
            )
    cells = pd.DataFrame(grid_rows).merge(
        observed,
        on=["AcquisitionCohort", "CohortIndex", "ActivityMonth"],
        how="left",
        validate="one_to_one",
    )
    cells[["ActiveCustomers", "Orders"]] = cells[["ActiveCustomers", "Orders"]].fillna(0).astype("int64")
    cells["Revenue"] = numeric(cells["Revenue"].fillna(0)).astype(float)
    cells["RetentionRate"] = cells["ActiveCustomers"] / cells["CohortSize"]
    cells["RevenuePerOriginalCustomer"] = cells["Revenue"] / cells["CohortSize"]
    cells["OrdersPerOriginalCustomer"] = cells["Orders"] / cells["CohortSize"]
    cells["IsPartialObservation"] = cells["ActivityMonth"].eq(observation_month)
    cells["ObservationStatus"] = np.where(
        cells["IsPartialObservation"], "PARTIAL_THROUGH_2011-12-09", "COMPLETE_MONTH"
    )
    return cells


def build_cohort_summary(cells: pd.DataFrame) -> pd.DataFrame:
    base = cells.groupby("AcquisitionCohort", observed=True).agg(
        CohortSize=("CohortSize", "first"),
        ObservedThroughIndex=("CohortIndex", "max"),
        LifecycleRevenue=("Revenue", "sum"),
        LifecycleOrders=("Orders", "sum"),
    ).reset_index()
    for month in CHECKPOINT_MONTHS:
        values = cells.loc[
            cells["CohortIndex"].eq(month) & ~cells["IsPartialObservation"],
            ["AcquisitionCohort", "RetentionRate"],
        ].rename(columns={"RetentionRate": f"Month{month}Retention"})
        base = base.merge(values, on="AcquisitionCohort", how="left", validate="one_to_one")
    base["IsLeftBoundaryCohort"] = base["AcquisitionCohort"].eq(pd.Period("2009-12"))
    base["IsPartialAcquisitionCohort"] = base["AcquisitionCohort"].eq(pd.Period("2011-12"))
    return base


def checkpoint_metrics(cells: pd.DataFrame) -> dict[str, Any]:
    results = {}
    for month in CHECKPOINT_MONTHS:
        eligible = cells.loc[
            cells["CohortIndex"].eq(month) & ~cells["IsPartialObservation"]
        ]
        results[f"month_{month}"] = {
            "eligible_cohorts": int(len(eligible)),
            "eligible_original_customers": int(eligible["CohortSize"].sum()),
            "active_customers": int(eligible["ActiveCustomers"].sum()),
            "cohort_size_weighted_retention": float(
                eligible["ActiveCustomers"].sum() / eligible["CohortSize"].sum()
            ),
            "median_cohort_retention": float(eligible["RetentionRate"].median()),
        }
    return results


def repeat_summary(customers: pd.DataFrame, observation_end: pd.Timestamp) -> dict[str, Any]:
    repeated = customers.loc[customers["HasRepeatPurchase"]].copy()
    days = repeated["DaysToSecondPurchase"].astype(float)
    windows = {}
    for window in [30, 60, 90, 180]:
        count = int(days.le(window).sum())
        windows[f"within_{window}_days"] = {
            "customers": count,
            "share_of_all_customers": count / len(customers),
            "share_of_repeat_customers": count / len(repeated),
        }
    return {
        "eligible_customers": int(len(customers)),
        "customers_with_second_purchase": int(len(repeated)),
        "customers_without_second_purchase": int((~customers["HasRepeatPurchase"]).sum()),
        "observed_repeat_purchase_rate": float(len(repeated) / len(customers)),
        "days_to_second_purchase": {
            "mean": float(days.mean()),
            "median": float(days.median()),
            "p25": float(days.quantile(0.25)),
            "p75": float(days.quantile(0.75)),
            "p90": float(days.quantile(0.90)),
        },
        "windows": windows,
        "right_censoring_note": (
            f"Observation ends {observation_end.date().isoformat()}; later acquisitions "
            "have less opportunity to record a second purchase."
        ),
    }


def validate(
    customers: pd.DataFrame,
    cells: pd.DataFrame,
    governed: dict[str, Any],
) -> list[dict[str, Any]]:
    month_zero = cells.loc[cells["CohortIndex"].eq(0)]
    checks = {
        "All governed customers have one customer row": len(customers) == int(governed["CustomerCount"]),
        "Expected approved customer population": len(customers) == EXPECTED_CUSTOMERS,
        "Every customer ID is unique": customers["CustomerID"].is_unique,
        "No anonymous customer IDs": customers["CustomerID"].notna().all(),
        "Every customer has one acquisition cohort": customers["AcquisitionCohort"].notna().all(),
        "Cohort sizes sum to governed customers": int(month_zero["CohortSize"].sum()) == int(governed["CustomerCount"]),
        "Month 0 active customers equal cohort size": month_zero["ActiveCustomers"].eq(month_zero["CohortSize"]).all(),
        "Month 0 retention is 100 percent": np.allclose(month_zero["RetentionRate"], 1.0),
        "No negative cohort index": cells["CohortIndex"].ge(0).all(),
        "No retention above 100 percent": cells["RetentionRate"].le(1.0).all(),
        "Cohort revenue reconciles to governed SQL": abs(cells["Revenue"].sum() - float(governed["Revenue"])) <= 0.0001,
        "Expected approved known-customer revenue": abs(cells["Revenue"].sum() - EXPECTED_REVENUE) <= 0.0001,
        "Cohort orders reconcile to governed SQL": int(cells["Orders"].sum()) == int(governed["OrderCount"]),
        "Expected approved known-customer orders": int(cells["Orders"].sum()) == EXPECTED_ORDERS,
    }
    return [
        {
            "check": name,
            "actual": bool(passed),
            "expected": True,
            "status": "PASS" if passed else "FAIL",
        }
        for name, passed in checks.items()
    ]


def create_figures(
    cells: pd.DataFrame,
    summary: pd.DataFrame,
    customers: pd.DataFrame,
) -> list[str]:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid")
    created = []

    def save(name: str) -> None:
        path = FIGURE_DIR / name
        plt.tight_layout()
        plt.savefig(path, dpi=160, bbox_inches="tight")
        plt.close()
        created.append(str(path.relative_to(PROJECT_ROOT)).replace("\\", "/"))

    pivot = cells.pivot(index="AcquisitionCohort", columns="CohortIndex", values="RetentionRate")
    plt.figure(figsize=(13, 8))
    image = plt.imshow(pivot.to_numpy(), aspect="auto", cmap="Blues", vmin=0, vmax=1)
    plt.colorbar(image, label="Retention rate")
    plt.yticks(range(len(pivot.index)), pivot.index.astype(str))
    plt.xticks(range(len(pivot.columns)), pivot.columns, rotation=0)
    plt.title("Customer Period Retention by Acquisition Cohort")
    plt.xlabel("Cohort index (months)")
    plt.ylabel("Acquisition cohort")
    save("cohort_customer_retention_heatmap.png")

    labels = summary["AcquisitionCohort"].astype(str)
    plt.figure(figsize=(12, 5))
    plt.bar(labels, summary["CohortSize"], color="#4c78a8")
    plt.xticks(rotation=60, ha="right")
    plt.title("Customer Acquisition Cohort Size")
    plt.xlabel("Acquisition month")
    plt.ylabel("Customers")
    save("cohort_size_by_month.png")

    plt.figure(figsize=(12, 5.5))
    for month, color in [(1, "#3b7f6d"), (3, "#aa6f39"), (6, "#735290")]:
        plt.plot(labels, summary[f"Month{month}Retention"] * 100, marker="o", label=f"Month {month}", color=color)
    plt.xticks(rotation=60, ha="right")
    plt.title("Observed Retention Trend by Acquisition Cohort")
    plt.xlabel("Acquisition month")
    plt.ylabel("Retention rate (%)")
    plt.legend()
    save("cohort_retention_checkpoint_trends.png")

    days = customers.loc[customers["HasRepeatPurchase"], "DaysToSecondPurchase"].astype(float)
    plt.figure(figsize=(9, 5))
    plt.hist(days, bins=50, color="#c04b50")
    plt.axvline(days.median(), color="#222222", linestyle="--", label=f"Median: {days.median():.0f} days")
    plt.title("Days to Second Eligible Purchase")
    plt.xlabel("Calendar days")
    plt.ylabel("Customers")
    plt.legend()
    save("customer_days_to_second_purchase.png")
    return created


def format_periods(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    for column in ["AcquisitionCohort", "ActivityMonth"]:
        if column in result:
            result[column] = result[column].astype(str)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server", default="localhost")
    parser.add_argument("--driver", default="ODBC Driver 18 for SQL Server")
    args = parser.parse_args()

    connection = connect_sql(args.server, args.driver)
    try:
        orders, governed = load_orders(connection)
    finally:
        connection.close()
    orders["PurchaseDate"] = pd.to_datetime(orders["PurchaseDate"])
    orders["Revenue"] = numeric(orders["Revenue"]).astype(float)
    orders["Units"] = numeric(orders["Units"]).astype("int64")
    observation_end = pd.Timestamp(governed["MaximumInvoiceDate"])
    observation_month = observation_end.to_period("M")

    customers = build_customer_timing(orders)
    cells = build_cohort_cells(orders, customers, observation_month)
    summary = build_cohort_summary(cells)
    retention_metrics = checkpoint_metrics(cells)
    repeats = repeat_summary(customers, observation_end)
    checks = validate(customers, cells, governed)
    figures = create_figures(cells, summary, customers)

    retention_columns = [
        "AcquisitionCohort", "CohortIndex", "ActivityMonth", "CohortSize",
        "ActiveCustomers", "RetentionRate", "IsPartialObservation", "ObservationStatus",
    ]
    revenue_columns = [
        "AcquisitionCohort", "CohortIndex", "ActivityMonth", "CohortSize",
        "Revenue", "RevenuePerOriginalCustomer", "Orders",
        "OrdersPerOriginalCustomer", "IsPartialObservation", "ObservationStatus",
    ]
    repeat_export = customers.copy()
    repeat_export["AcquisitionCohort"] = repeat_export["AcquisitionCohort"].astype(str)
    repeat_export["FirstPurchaseDate"] = repeat_export["FirstPurchaseDate"].dt.strftime("%Y-%m-%d %H:%M:%S")
    repeat_export["SecondPurchaseDate"] = repeat_export["SecondPurchaseDate"].dt.strftime("%Y-%m-%d %H:%M:%S")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    format_periods(cells[retention_columns]).to_csv(
        OUTPUT_DIR / "cohort_customer_retention.csv", index=False, float_format="%.12g"
    )
    format_periods(cells[revenue_columns]).to_csv(
        OUTPUT_DIR / "cohort_revenue.csv", index=False, float_format="%.12g"
    )
    repeat_export.sort_values("CustomerID").to_csv(
        OUTPUT_DIR / "customer_repeat_timing.csv", index=False, float_format="%.12g"
    )
    format_periods(summary).to_csv(
        OUTPUT_DIR / "cohort_summary.csv", index=False, float_format="%.12g"
    )
    validation_payload = {
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
        "observation_window": {
            "start": pd.Timestamp(governed["MinimumInvoiceDate"]).isoformat(),
            "end": observation_end.isoformat(),
            "left_boundary_cohort": "2009-12",
            "partial_final_month": "2011-12 through 2011-12-09",
        },
        "cohort_count": int(customers["AcquisitionCohort"].nunique()),
        "retention_checkpoint_metrics": retention_metrics,
        "repeat_purchase_summary": repeats,
        "checks": checks,
        "figures": figures,
    }
    (OUTPUT_DIR / "cohort_validation.json").write_text(
        json.dumps(validation_payload, indent=2, default=json_value) + "\n",
        encoding="utf-8",
    )
    print(f"Cohorts: {validation_payload['cohort_count']}")
    print(json.dumps(retention_metrics, indent=2))
    print(json.dumps(repeats, indent=2))
    print(f"Validation: {validation_payload['status']}")
    return 0 if validation_payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
