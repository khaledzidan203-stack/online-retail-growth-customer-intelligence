"""Checkpoint 5A SQL-sourced Python validation, EDA, and sensitivity analysis."""

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

from validation import (
    connect_sql,
    distribution_record,
    json_value,
    numeric,
    query_frame,
    validation_records,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "outputs"
FIGURE_DIR = OUTPUT_DIR / "figures"

EXPECTED_KPIS = {
    "Sales Revenue": 19_701_685.507,
    "Units Sold": 11_221_960,
    "Orders": 39_519,
    "Sales-known customers": 5_852,
    "Average Order Value": 498.53704564,
    "Known-customer sales revenue": 17_125_672.047,
    "Repeat customers": 4_234,
    "One-time customers": 1_618,
    "Cancellation Value": 719_692.94,
    "Cancellation Invoices": 7_406,
    "Cancellation Value Rate": 0.035242,
}


def load_frames(connection: Any) -> dict[str, pd.DataFrame]:
    queries = {
        "orders": """
            SELECT
                Invoice,
                SUM(LineAmount) AS OrderRevenue,
                SUM(CONVERT(BIGINT, Quantity)) AS OrderUnits,
                COUNT(DISTINCT ProductKey) AS DistinctProducts,
                SUM(CASE WHEN CustomerKey IS NOT NULL THEN 1 ELSE 0 END)
                    AS KnownLines,
                SUM(CASE WHEN CustomerKey IS NULL THEN 1 ELSE 0 END)
                    AS AnonymousLines
            FROM analytics.FactTransaction
            WHERE IsSalesEligible = 1
            GROUP BY Invoice;
        """,
        "customers": """
            SELECT
                customer.CustomerID,
                SUM(fact.LineAmount) AS CustomerRevenue,
                COUNT(DISTINCT fact.Invoice) AS CustomerOrders,
                SUM(CONVERT(BIGINT, fact.Quantity)) AS CustomerUnits,
                MIN(CONVERT(DATE, fact.InvoiceDate)) AS FirstPurchaseDate,
                MAX(CONVERT(DATE, fact.InvoiceDate)) AS LastPurchaseDate,
                DATEDIFF(
                    DAY,
                    MIN(CONVERT(DATE, fact.InvoiceDate)),
                    MAX(CONVERT(DATE, fact.InvoiceDate))
                ) AS LifespanDays
            FROM analytics.FactTransaction AS fact
            INNER JOIN analytics.DimCustomer AS customer
                ON customer.CustomerKey = fact.CustomerKey
            WHERE fact.IsCustomerAnalyticsEligible = 1
            GROUP BY customer.CustomerID;
        """,
        "interpurchase": """
            WITH CustomerOrders AS
            (
                SELECT DISTINCT
                    CustomerKey,
                    Invoice,
                    CONVERT(DATE, InvoiceDate) AS OrderDate
                FROM analytics.FactTransaction
                WHERE IsCustomerAnalyticsEligible = 1
            ),
            Sequenced AS
            (
                SELECT
                    CustomerKey,
                    Invoice,
                    OrderDate,
                    LAG(OrderDate) OVER
                    (
                        PARTITION BY CustomerKey
                        ORDER BY OrderDate, Invoice
                    ) AS PreviousOrderDate
                FROM CustomerOrders
            )
            SELECT
                CustomerKey,
                DATEDIFF(DAY, PreviousOrderDate, OrderDate)
                    AS InterpurchaseDays
            FROM Sequenced
            WHERE PreviousOrderDate IS NOT NULL;
        """,
        "products": """
            SELECT
                product.StockCode,
                product.RepresentativeDescription,
                SUM(fact.LineAmount) AS ProductRevenue,
                SUM(CONVERT(BIGINT, fact.Quantity)) AS ProductUnits,
                COUNT(DISTINCT fact.Invoice) AS ProductOrders,
                COUNT(DISTINCT fact.CustomerKey) AS KnownCustomers,
                SUM(fact.LineAmount)
                    / NULLIF(SUM(CONVERT(BIGINT, fact.Quantity)), 0)
                    AS AverageSellingPrice
            FROM analytics.FactTransaction AS fact
            INNER JOIN analytics.DimProduct AS product
                ON product.ProductKey = fact.ProductKey
            WHERE fact.IsSalesEligible = 1
              AND product.ItemClass = N'MERCHANDISE'
            GROUP BY
                product.StockCode,
                product.RepresentativeDescription;
        """,
        "countries": """
            SELECT
                country.Country,
                SUM(fact.LineAmount) AS CountryRevenue,
                COUNT(DISTINCT fact.Invoice) AS CountryOrders,
                COUNT(DISTINCT fact.CustomerKey) AS KnownCustomers,
                SUM(fact.LineAmount)
                    / NULLIF(COUNT(DISTINCT fact.Invoice), 0) AS AOV
            FROM analytics.FactTransaction AS fact
            INNER JOIN analytics.DimCountry AS country
                ON country.CountryKey = fact.CountryKey
            WHERE fact.IsSalesEligible = 1
            GROUP BY country.Country;
        """,
        "cancellations": """
            SELECT
                fact.TransactionLineKey,
                fact.Invoice,
                fact.InvoiceDate,
                product.StockCode,
                customer.CustomerID,
                country.Country,
                fact.Quantity,
                fact.Price,
                fact.LineAmount,
                fact.IsExactDuplicateAfterFirst
            FROM analytics.FactTransaction AS fact
            INNER JOIN analytics.DimProduct AS product
                ON product.ProductKey = fact.ProductKey
            INNER JOIN analytics.DimCountry AS country
                ON country.CountryKey = fact.CountryKey
            LEFT JOIN analytics.DimCustomer AS customer
                ON customer.CustomerKey = fact.CustomerKey
            WHERE fact.IsCancellationEligible = 1;
        """,
        "anomaly": """
            SELECT
                fact.TransactionLineKey,
                fact.Invoice,
                fact.InvoiceDate,
                product.StockCode,
                product.RepresentativeDescription,
                customer.CustomerID,
                country.Country,
                fact.Quantity,
                fact.Price,
                fact.LineAmount,
                fact.TransactionClass,
                fact.IsExactDuplicateAfterFirst
            FROM analytics.FactTransaction AS fact
            INNER JOIN analytics.DimProduct AS product
                ON product.ProductKey = fact.ProductKey
            INNER JOIN analytics.DimCountry AS country
                ON country.CountryKey = fact.CountryKey
            LEFT JOIN analytics.DimCustomer AS customer
                ON customer.CustomerKey = fact.CustomerKey
            WHERE product.StockCode = N'23843'
               OR customer.CustomerID = N'16446'
            ORDER BY fact.InvoiceDate, fact.TransactionLineKey;
        """,
        "daily": """
            SELECT
                date_dimension.FullDate,
                SUM(CASE WHEN fact.IsSalesEligible = 1
                    THEN fact.LineAmount ELSE 0 END) AS SalesRevenue,
                SUM(CASE WHEN fact.IsSalesEligible = 1
                    THEN CONVERT(BIGINT, fact.Quantity) ELSE 0 END) AS Units,
                COUNT(DISTINCT CASE WHEN fact.IsSalesEligible = 1
                    THEN fact.Invoice END) AS Orders,
                SUM(CASE WHEN fact.IsCancellationEligible = 1
                    THEN ABS(fact.LineAmount) ELSE 0 END)
                    AS CancellationValue
            FROM analytics.DimDate AS date_dimension
            LEFT JOIN analytics.FactTransaction AS fact
                ON fact.DateKey = date_dimension.DateKey
            GROUP BY date_dimension.FullDate
            ORDER BY date_dimension.FullDate;
        """,
        "monthly": """
            SELECT * FROM analytics.vw_MonthlyPerformance
            ORDER BY PeriodStart;
        """,
        "missing_customer": """
            SELECT
                IsKnownCustomer,
                SUM(LineAmount) AS Revenue,
                SUM(CONVERT(BIGINT, Quantity)) AS Units,
                COUNT(DISTINCT Invoice) AS Orders,
                COUNT_BIG(*) AS Lines
            FROM analytics.FactTransaction
            WHERE IsSalesEligible = 1
            GROUP BY IsKnownCustomer;
        """,
        "duplicate_sensitivity": """
            SELECT
                N'Official' AS Scenario,
                SUM(CASE WHEN IsSalesEligible = 1
                    THEN LineAmount ELSE 0 END) AS Revenue,
                SUM(CASE WHEN IsSalesEligible = 1
                    THEN CONVERT(BIGINT, Quantity) ELSE 0 END) AS Units,
                COUNT(DISTINCT CASE WHEN IsSalesEligible = 1
                    THEN Invoice END) AS Orders,
                SUM(CASE WHEN IsCancellationEligible = 1
                    THEN ABS(LineAmount) ELSE 0 END) AS CancellationValue
            FROM analytics.FactTransaction
            UNION ALL
            SELECT
                N'Exclude duplicate-after-first',
                SUM(CASE WHEN IsSalesEligible = 1
                    THEN LineAmount ELSE 0 END),
                SUM(CASE WHEN IsSalesEligible = 1
                    THEN CONVERT(BIGINT, Quantity) ELSE 0 END),
                COUNT(DISTINCT CASE WHEN IsSalesEligible = 1
                    THEN Invoice END),
                SUM(CASE WHEN IsCancellationEligible = 1
                    THEN ABS(LineAmount) ELSE 0 END)
            FROM analytics.FactTransaction
            WHERE IsExactDuplicateAfterFirst = 0;
        """,
    }
    return {
        name: query_frame(connection, query)
        for name, query in queries.items()
    }


def calculate_validation(
    frames: dict[str, pd.DataFrame],
) -> tuple[list[dict[str, Any]], dict[str, float | int]]:
    orders = frames["orders"]
    customers = frames["customers"]
    cancellations = frames["cancellations"]
    sales_revenue = float(numeric(orders["OrderRevenue"]).sum())
    cancellation_value = float(
        numeric(cancellations["LineAmount"]).abs().sum()
    )
    actual = {
        "Sales Revenue": sales_revenue,
        "Units Sold": int(numeric(orders["OrderUnits"]).sum()),
        "Orders": int(len(orders)),
        "Sales-known customers": int(len(customers)),
        "Average Order Value": sales_revenue / len(orders),
        "Known-customer sales revenue": float(
            numeric(customers["CustomerRevenue"]).sum()
        ),
        "Repeat customers": int(
            numeric(customers["CustomerOrders"]).gt(1).sum()
        ),
        "One-time customers": int(
            numeric(customers["CustomerOrders"]).eq(1).sum()
        ),
        "Cancellation Value": cancellation_value,
        "Cancellation Invoices": int(
            cancellations["Invoice"].nunique()
        ),
        "Cancellation Value Rate": (
            cancellation_value / (sales_revenue + cancellation_value)
        ),
    }
    return validation_records(actual, EXPECTED_KPIS), actual


def calculate_distributions(
    frames: dict[str, pd.DataFrame],
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    cancellations = frames["cancellations"].copy()
    cancellations["CancellationValue"] = numeric(
        cancellations["LineAmount"]
    ).abs()
    cancellations["CancellationUnits"] = numeric(
        cancellations["Quantity"]
    ).abs()
    cancellations["InvoiceDate"] = pd.to_datetime(
        cancellations["InvoiceDate"]
    )
    cancel_aggregates = {
        "Cancellation invoice": cancellations.groupby("Invoice").agg(
            Value=("CancellationValue", "sum"),
            Units=("CancellationUnits", "sum"),
        ),
        "Cancellation customer": cancellations.dropna(
            subset=["CustomerID"]
        ).groupby("CustomerID").agg(
            Value=("CancellationValue", "sum"),
            Units=("CancellationUnits", "sum"),
        ),
        "Cancellation product": cancellations.groupby("StockCode").agg(
            Value=("CancellationValue", "sum"),
            Units=("CancellationUnits", "sum"),
        ),
        "Cancellation country": cancellations.groupby("Country").agg(
            Value=("CancellationValue", "sum"),
            Units=("CancellationUnits", "sum"),
        ),
        "Cancellation month": cancellations.assign(
            Month=cancellations["InvoiceDate"].dt.to_period("M").astype(str)
        ).groupby("Month").agg(
            Value=("CancellationValue", "sum"),
            Units=("CancellationUnits", "sum"),
        ),
    }
    definitions = [
        ("Order", "Revenue", frames["orders"]["OrderRevenue"]),
        ("Order", "Units", frames["orders"]["OrderUnits"]),
        (
            "Order",
            "Distinct products",
            frames["orders"]["DistinctProducts"],
        ),
        (
            "Customer",
            "Revenue",
            frames["customers"]["CustomerRevenue"],
        ),
        (
            "Customer",
            "Orders",
            frames["customers"]["CustomerOrders"],
        ),
        ("Customer", "Units", frames["customers"]["CustomerUnits"]),
        (
            "Customer",
            "Lifespan days",
            frames["customers"]["LifespanDays"],
        ),
        (
            "Customer",
            "Interpurchase days",
            frames["interpurchase"]["InterpurchaseDays"],
        ),
        (
            "Product",
            "Revenue",
            frames["products"]["ProductRevenue"],
        ),
        ("Product", "Units", frames["products"]["ProductUnits"]),
        ("Product", "Orders", frames["products"]["ProductOrders"]),
        (
            "Product",
            "Known customers",
            frames["products"]["KnownCustomers"],
        ),
        (
            "Product",
            "Average selling price",
            frames["products"]["AverageSellingPrice"],
        ),
        (
            "Country",
            "Revenue",
            frames["countries"]["CountryRevenue"],
        ),
        ("Country", "Orders", frames["countries"]["CountryOrders"]),
        (
            "Country",
            "Known customers",
            frames["countries"]["KnownCustomers"],
        ),
        ("Country", "AOV", frames["countries"]["AOV"]),
        (
            "Cancellation line",
            "Value",
            cancellations["CancellationValue"],
        ),
        (
            "Cancellation line",
            "Units",
            cancellations["CancellationUnits"],
        ),
    ]
    for grain, aggregate in cancel_aggregates.items():
        definitions.extend(
            [
                (grain, "Value", aggregate["Value"]),
                (grain, "Units", aggregate["Units"]),
            ]
        )
    records = [
        distribution_record(grain, metric, values)
        for grain, metric, values in definitions
    ]
    return pd.DataFrame(records), cancel_aggregates


def calculate_sensitivities(
    frames: dict[str, pd.DataFrame],
) -> tuple[pd.DataFrame, dict[str, Any], dict[str, Any]]:
    duplicate = frames["duplicate_sensitivity"].copy()
    for column in ["Revenue", "Units", "Orders", "CancellationValue"]:
        duplicate[column] = numeric(duplicate[column])
    duplicate["AOV"] = duplicate["Revenue"] / duplicate["Orders"]
    official = duplicate.loc[duplicate["Scenario"].eq("Official")].iloc[0]
    excluded = duplicate.loc[
        duplicate["Scenario"].eq("Exclude duplicate-after-first")
    ].iloc[0]
    rows = []
    for metric in [
        "Revenue",
        "Units",
        "Orders",
        "AOV",
        "CancellationValue",
    ]:
        difference = float(excluded[metric] - official[metric])
        rows.append(
            {
                "sensitivity": "Duplicate-after-first exclusion",
                "metric": metric,
                "official_value": float(official[metric]),
                "comparison_value": float(excluded[metric]),
                "absolute_difference": difference,
                "percent_impact": (
                    difference / float(official[metric])
                    if float(official[metric]) != 0
                    else None
                ),
            }
        )

    missing = frames["missing_customer"].copy()
    for column in ["Revenue", "Units", "Orders", "Lines"]:
        missing[column] = numeric(missing[column])
    total_revenue = float(missing["Revenue"].sum())
    missing_summary = {}
    for _, record in missing.iterrows():
        label = "known" if bool(record["IsKnownCustomer"]) else "anonymous"
        missing_summary[label] = {
            "revenue": float(record["Revenue"]),
            "units": int(record["Units"]),
            "orders": int(record["Orders"]),
            "lines": int(record["Lines"]),
            "revenue_share": float(record["Revenue"]) / total_revenue,
            "average_order_value": (
                float(record["Revenue"]) / int(record["Orders"])
            ),
        }
    orders = frames["orders"]
    missing_summary["mixed_known_anonymous_orders"] = int(
        (
            numeric(orders["KnownLines"]).gt(0)
            & numeric(orders["AnonymousLines"]).gt(0)
        ).sum()
    )

    cancellations = frames["cancellations"].copy()
    cancellations["CancellationValue"] = numeric(
        cancellations["LineAmount"]
    ).abs()
    cancellations["InvoiceDate"] = pd.to_datetime(
        cancellations["InvoiceDate"]
    )
    event_mask = (
        cancellations["StockCode"].astype(str).eq("23843")
        & cancellations["CustomerID"].astype(str).eq("16446")
    )
    event = cancellations.loc[event_mask]
    official_cancel = float(cancellations["CancellationValue"].sum())
    event_value = float(event["CancellationValue"].sum())
    december_mask = cancellations["InvoiceDate"].dt.to_period("M").eq(
        pd.Period("2011-12")
    )
    december_value = float(
        cancellations.loc[december_mask, "CancellationValue"].sum()
    )
    monthly_values = cancellations.groupby(
        cancellations["InvoiceDate"].dt.to_period("M")
    )["CancellationValue"].sum()
    adjusted_monthly_values = monthly_values.copy()
    adjusted_monthly_values.loc[pd.Period("2011-12")] -= event_value
    official_top_month = monthly_values.idxmax()
    adjusted_top_month = adjusted_monthly_values.idxmax()
    anomaly_summary = {
        "event_rows": int(len(event)),
        "event_invoices": int(event["Invoice"].nunique()),
        "event_value": event_value,
        "share_of_total_cancellation_value": (
            event_value / official_cancel
        ),
        "cancellation_value_without_event": (
            official_cancel - event_value
        ),
        "official_cancellation_value_rate": (
            official_cancel
            / (EXPECTED_KPIS["Sales Revenue"] + official_cancel)
        ),
        "cancellation_value_rate_without_event": (
            (official_cancel - event_value)
            / (
                EXPECTED_KPIS["Sales Revenue"]
                + official_cancel
                - event_value
            )
        ),
        "december_2011_cancellation_value": december_value,
        "december_2011_value_without_event": (
            december_value - event_value
        ),
        "december_event_share": event_value / december_value,
        "official_highest_cancellation_month": str(official_top_month),
        "official_highest_month_value": float(
            monthly_values.loc[official_top_month]
        ),
        "highest_month_without_event": str(adjusted_top_month),
        "highest_month_value_without_event": float(
            adjusted_monthly_values.loc[adjusted_top_month]
        ),
        "december_remains_highest_without_event": (
            adjusted_top_month == pd.Period("2011-12")
        ),
    }
    rows.append(
        {
            "sensitivity": "StockCode 23843 / Customer 16446 exclusion",
            "metric": "CancellationValue",
            "official_value": official_cancel,
            "comparison_value": official_cancel - event_value,
            "absolute_difference": -event_value,
            "percent_impact": -event_value / official_cancel,
        }
    )
    return pd.DataFrame(rows), missing_summary, anomaly_summary


def forecasting_readiness(
    daily: pd.DataFrame, monthly: pd.DataFrame
) -> dict[str, Any]:
    daily = daily.copy()
    daily["FullDate"] = pd.to_datetime(daily["FullDate"])
    daily["SalesRevenue"] = numeric(daily["SalesRevenue"]).astype(float)
    daily = daily.sort_values("FullDate").set_index("FullDate")
    complete_index = pd.date_range(daily.index.min(), daily.index.max())
    weekly = daily["SalesRevenue"].resample("W-SUN").sum()
    monthly_revenue = numeric(monthly["SalesRevenue"]).astype(float)
    monthly_slope = float(
        np.polyfit(np.arange(len(monthly_revenue)), monthly_revenue, 1)[0]
    )
    day_means = daily.groupby(daily.index.dayofweek)[
        "SalesRevenue"
    ].mean()
    return {
        "status": "CONDITIONAL",
        "evidence": {
            "start_date": daily.index.min().date().isoformat(),
            "end_date": daily.index.max().date().isoformat(),
            "covered_calendar_days": int(len(daily)),
            "expected_calendar_days": int(len(complete_index)),
            "missing_calendar_dates": int(
                len(complete_index.difference(daily.index))
            ),
            "zero_revenue_days": int(daily["SalesRevenue"].eq(0).sum()),
            "daily_revenue_p99": float(
                daily["SalesRevenue"].quantile(0.99)
            ),
            "daily_revenue_max": float(daily["SalesRevenue"].max()),
            "daily_max_to_p99_ratio": float(
                daily["SalesRevenue"].max()
                / daily["SalesRevenue"].quantile(0.99)
            ),
            "weekly_observations": int(len(weekly)),
            "weekly_revenue_p99": float(weekly.quantile(0.99)),
            "weekly_revenue_max": float(weekly.max()),
            "daily_lag7_autocorrelation": float(
                daily["SalesRevenue"].autocorr(lag=7)
            ),
            "daily_lag28_autocorrelation": float(
                daily["SalesRevenue"].autocorr(lag=28)
            ),
            "daily_lag365_autocorrelation": float(
                daily["SalesRevenue"].autocorr(lag=365)
            ),
            "monthly_linear_slope": monthly_slope,
            "weekday_mean_max_to_min_ratio": float(
                day_means.max() / day_means.min()
            ),
        },
        "reasons": [
            "Daily coverage is complete enough to construct regular series.",
            "The history is only about two years and has partial boundary periods.",
            "Extreme wholesale transactions and cancellations create material spikes.",
            "Trend and recurring calendar patterns exist but require robust treatment and backtesting.",
        ],
        "forecast_created": False,
    }


def create_figures(
    frames: dict[str, pd.DataFrame],
    sensitivity: pd.DataFrame,
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

    monthly = frames["monthly"].copy()
    monthly["PeriodStart"] = pd.to_datetime(monthly["PeriodStart"])
    plt.figure(figsize=(10, 4.8))
    plt.plot(
        monthly["PeriodStart"],
        numeric(monthly["SalesRevenue"]),
        color="#255f85",
        linewidth=2,
    )
    plt.title("Monthly Merchandise Sales Revenue")
    plt.xlabel("Month")
    plt.ylabel("Revenue (source currency)")
    save("checkpoint5a_monthly_revenue.png")

    order_revenue = numeric(frames["orders"]["OrderRevenue"]).astype(float)
    plt.figure(figsize=(8, 4.8))
    plt.hist(np.log10(order_revenue), bins=60, color="#3b7f6d")
    plt.title("Order Revenue Distribution (Log Scale)")
    plt.xlabel("log10(Order Revenue)")
    plt.ylabel("Orders")
    save("checkpoint5a_order_revenue_distribution.png")

    customer_revenue = numeric(
        frames["customers"]["CustomerRevenue"]
    ).astype(float)
    plt.figure(figsize=(8, 4.8))
    plt.hist(np.log10(customer_revenue), bins=60, color="#735290")
    plt.title("Known-Customer Revenue Distribution (Log Scale)")
    plt.xlabel("log10(Customer Revenue)")
    plt.ylabel("Customers")
    save("checkpoint5a_customer_revenue_distribution.png")

    customer_orders = numeric(frames["customers"]["CustomerOrders"])
    plt.figure(figsize=(8, 4.8))
    plt.hist(customer_orders, bins=60, color="#aa6f39")
    plt.yscale("log")
    plt.title("Orders per Known Customer")
    plt.xlabel("Distinct eligible orders")
    plt.ylabel("Customers (log scale)")
    save("checkpoint5a_customer_order_distribution.png")

    product_revenue = numeric(
        frames["products"]["ProductRevenue"]
    ).sort_values(ascending=False)
    cumulative = product_revenue.cumsum() / product_revenue.sum()
    plt.figure(figsize=(8, 4.8))
    plt.plot(
        np.arange(1, len(cumulative) + 1),
        cumulative,
        color="#b44c43",
    )
    for threshold in [0.5, 0.8, 0.9]:
        plt.axhline(threshold, color="#777777", linestyle="--", linewidth=0.8)
    plt.title("Product Revenue Concentration")
    plt.xlabel("Products ranked by revenue")
    plt.ylabel("Cumulative revenue share")
    save("checkpoint5a_product_concentration.png")

    country = frames["countries"].copy()
    country["CountryRevenue"] = numeric(country["CountryRevenue"])
    country = country.sort_values("CountryRevenue", ascending=False)
    top = country.head(10).copy()
    other = country.iloc[10:]["CountryRevenue"].sum()
    labels = top["Country"].tolist() + ["Other"]
    values = top["CountryRevenue"].tolist() + [other]
    plt.figure(figsize=(9, 5.2))
    plt.barh(labels[::-1], values[::-1], color="#4c78a8")
    plt.title("Country Merchandise Revenue Concentration")
    plt.xlabel("Revenue (source currency)")
    save("checkpoint5a_country_revenue.png")

    cancellations = frames["cancellations"].copy()
    cancellations["InvoiceDate"] = pd.to_datetime(
        cancellations["InvoiceDate"]
    )
    cancellations["Value"] = numeric(
        cancellations["LineAmount"]
    ).abs()
    monthly_cancel = cancellations.groupby(
        cancellations["InvoiceDate"].dt.to_period("M")
    )["Value"].sum()
    plt.figure(figsize=(10, 4.8))
    plt.plot(
        monthly_cancel.index.astype(str),
        monthly_cancel.values,
        color="#c04b50",
        linewidth=2,
    )
    plt.xticks(rotation=60, ha="right")
    plt.title("Monthly Customer Cancellation Value")
    plt.xlabel("Month")
    plt.ylabel("Absolute cancellation value")
    save("checkpoint5a_cancellation_distribution.png")

    duplicate = sensitivity.loc[
        sensitivity["sensitivity"].eq("Duplicate-after-first exclusion")
    ].copy()
    plt.figure(figsize=(8, 4.8))
    plt.bar(
        duplicate["metric"],
        duplicate["percent_impact"] * 100,
        color="#6d8494",
    )
    plt.axhline(0, color="#333333", linewidth=0.8)
    plt.xticks(rotation=25, ha="right")
    plt.title("Sensitivity to Excluding Duplicate-After-First Rows")
    plt.ylabel("Change versus official KPI (%)")
    save("checkpoint5a_duplicate_sensitivity.png")
    return created


def find_distribution(
    distributions: pd.DataFrame, grain: str, metric: str
) -> dict[str, Any]:
    record = distributions.loc[
        distributions["grain"].eq(grain)
        & distributions["metric"].eq(metric)
    ].iloc[0]
    return {
        key: json_value(value)
        for key, value in record.to_dict().items()
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server", default="localhost")
    parser.add_argument("--driver", default="ODBC Driver 18 for SQL Server")
    args = parser.parse_args()

    connection = connect_sql(args.server, args.driver)
    try:
        frames = load_frames(connection)
    finally:
        connection.close()

    validation, actual_kpis = calculate_validation(frames)
    distributions, _ = calculate_distributions(frames)
    sensitivity, missing_summary, anomaly_summary = (
        calculate_sensitivities(frames)
    )
    forecast = forecasting_readiness(
        frames["daily"], frames["monthly"]
    )
    figures = create_figures(frames, sensitivity)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(validation).to_csv(
        OUTPUT_DIR / "checkpoint5a_python_validation.csv", index=False
    )
    distributions.to_csv(
        OUTPUT_DIR / "checkpoint5a_distribution_summary.csv", index=False
    )
    frames["anomaly"].to_csv(
        OUTPUT_DIR / "checkpoint5a_anomaly_analysis.csv", index=False
    )
    sensitivity.to_csv(
        OUTPUT_DIR / "checkpoint5a_sensitivity_analysis.csv", index=False
    )
    (OUTPUT_DIR / "checkpoint5a_forecasting_readiness.json").write_text(
        json.dumps(forecast, indent=2) + "\n", encoding="utf-8"
    )

    products = frames["products"].copy()
    products["ProductRevenue"] = numeric(products["ProductRevenue"])
    products["ProductUnits"] = numeric(products["ProductUnits"])
    customers = frames["customers"].copy()
    customers["CustomerRevenue"] = numeric(customers["CustomerRevenue"])
    customers["CustomerOrders"] = numeric(customers["CustomerOrders"])
    anomaly_records = [
        {key: json_value(value) for key, value in record.items()}
        for record in frames["anomaly"].to_dict("records")
    ]
    summary = {
        "validation_status": (
            "PASS"
            if all(row["status"] == "PASS" for row in validation)
            else "FAIL"
        ),
        "validations": validation,
        "python_kpis": actual_kpis,
        "distribution_highlights": {
            "order_revenue": find_distribution(
                distributions, "Order", "Revenue"
            ),
            "order_units": find_distribution(
                distributions, "Order", "Units"
            ),
            "customer_revenue": find_distribution(
                distributions, "Customer", "Revenue"
            ),
            "customer_orders": find_distribution(
                distributions, "Customer", "Orders"
            ),
            "customer_lifespan": find_distribution(
                distributions, "Customer", "Lifespan days"
            ),
            "interpurchase_days": find_distribution(
                distributions, "Customer", "Interpurchase days"
            ),
            "product_revenue": find_distribution(
                distributions, "Product", "Revenue"
            ),
            "product_units": find_distribution(
                distributions, "Product", "Units"
            ),
        },
        "extremes": {
            "highest_revenue_product": {
                key: json_value(value)
                for key, value in products.sort_values(
                    "ProductRevenue", ascending=False
                ).iloc[0].to_dict().items()
            },
            "highest_units_product": {
                key: json_value(value)
                for key, value in products.sort_values(
                    "ProductUnits", ascending=False
                ).iloc[0].to_dict().items()
            },
            "highest_revenue_customer": {
                key: json_value(value)
                for key, value in customers.sort_values(
                    "CustomerRevenue", ascending=False
                ).iloc[0].to_dict().items()
            },
            "highest_frequency_customer": {
                key: json_value(value)
                for key, value in customers.sort_values(
                    "CustomerOrders", ascending=False
                ).iloc[0].to_dict().items()
            },
        },
        "missing_customer_sensitivity": missing_summary,
        "anomaly_summary": anomaly_summary,
        "anomaly_records": anomaly_records,
        "duplicate_sensitivity": sensitivity.to_dict("records"),
        "forecasting_readiness": forecast,
        "figures": figures,
    }
    summary_path = OUTPUT_DIR / "checkpoint5a_eda_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, default=json_value) + "\n",
        encoding="utf-8",
    )
    print(f"Validation: {summary['validation_status']}")
    print(f"Distribution metrics: {len(distributions)}")
    print(f"Figures: {len(figures)}")
    print(f"Forecasting readiness: {forecast['status']}")
    print(f"Output: {summary_path.resolve()}")
    return 0 if summary["validation_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
