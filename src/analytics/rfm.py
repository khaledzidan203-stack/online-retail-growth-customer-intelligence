"""Build the governed Checkpoint 5B RFM customer segmentation."""

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

SEGMENT_ORDER = [
    "Champions",
    "Loyal Customers",
    "Potential Loyalists",
    "New Customers",
    "Promising",
    "Need Attention",
    "At Risk",
    "Hibernating",
    "Lost",
]


def load_customer_rfm(connection: Any) -> tuple[pd.DataFrame, dict[str, Any]]:
    customers = query_frame(
        connection,
        """
        SELECT
            customer.CustomerID,
            MIN(fact.InvoiceDate) AS FirstPurchaseDate,
            MAX(fact.InvoiceDate) AS LastPurchaseDate,
            COUNT(DISTINCT fact.Invoice) AS Frequency,
            SUM(fact.LineAmount) AS Monetary,
            SUM(CONVERT(BIGINT, fact.Quantity)) AS UnitsPurchased
        FROM analytics.FactTransaction AS fact
        INNER JOIN analytics.DimCustomer AS customer
            ON customer.CustomerKey = fact.CustomerKey
        WHERE fact.IsCustomerAnalyticsEligible = 1
        GROUP BY customer.CustomerID;
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
            MAX(InvoiceDate) AS MaximumInvoiceDate
        FROM analytics.FactTransaction
        WHERE IsCustomerAnalyticsEligible = 1;
        """,
    ).iloc[0]
    return customers, governed.to_dict()


def tied_quantile_score(values: pd.Series, higher_is_better: bool) -> pd.Series:
    """Score from observed quintile cutpoints without splitting tied values."""
    measure = numeric(values).astype(float)
    cutpoints = np.unique(measure.quantile([0.2, 0.4, 0.6, 0.8]).to_numpy())
    band = np.searchsorted(cutpoints, measure.to_numpy(), side="left")
    score = band + 1 if higher_is_better else len(cutpoints) + 1 - band
    return pd.Series(score, index=values.index, dtype="int64").clip(1, 5)


def assign_segment(row: pd.Series) -> str:
    r_score = int(row["R_Score"])
    f_score = int(row["F_Score"])
    m_score = int(row["M_Score"])
    if r_score >= 4 and f_score >= 4 and m_score >= 4:
        return "Champions"
    if r_score >= 3 and f_score >= 4:
        return "Loyal Customers"
    if r_score >= 4 and 2 <= f_score <= 3:
        return "Potential Loyalists"
    if r_score == 5 and f_score == 1:
        return "New Customers"
    if (r_score == 4 and f_score == 1) or (
        r_score == 3 and 2 <= f_score <= 3 and m_score >= 3
    ):
        return "Promising"
    if r_score == 3:
        return "Need Attention"
    if r_score <= 2 and f_score >= 3:
        return "At Risk"
    if r_score == 2 and f_score <= 2:
        return "Hibernating"
    return "Lost"


def build_rfm(customers: pd.DataFrame, maximum_invoice_date: Any) -> tuple[pd.DataFrame, pd.Timestamp]:
    frame = customers.copy()
    frame["FirstPurchaseDate"] = pd.to_datetime(frame["FirstPurchaseDate"])
    frame["LastPurchaseDate"] = pd.to_datetime(frame["LastPurchaseDate"])
    frame["Frequency"] = numeric(frame["Frequency"]).astype("int64")
    frame["Monetary"] = numeric(frame["Monetary"]).astype(float)
    frame["UnitsPurchased"] = numeric(frame["UnitsPurchased"]).astype("int64")
    reference_date = pd.Timestamp(maximum_invoice_date).normalize() + pd.Timedelta(days=1)
    frame["Recency"] = (reference_date - frame["LastPurchaseDate"].dt.normalize()).dt.days
    frame["ActiveLifespanDays"] = (
        frame["LastPurchaseDate"].dt.normalize()
        - frame["FirstPurchaseDate"].dt.normalize()
    ).dt.days
    frame["AverageOrderValue"] = frame["Monetary"] / frame["Frequency"]
    frame["R_Score"] = tied_quantile_score(frame["Recency"], higher_is_better=False)
    frame["F_Score"] = tied_quantile_score(frame["Frequency"], higher_is_better=True)
    frame["M_Score"] = tied_quantile_score(frame["Monetary"], higher_is_better=True)
    frame["RFM_Code"] = (
        frame["R_Score"].astype(str)
        + frame["F_Score"].astype(str)
        + frame["M_Score"].astype(str)
    )
    frame["RFM_Total"] = frame[["R_Score", "F_Score", "M_Score"]].sum(axis=1)
    frame["Segment"] = frame.apply(assign_segment, axis=1)
    return frame, reference_date


def score_boundaries(frame: pd.DataFrame, reference_date: pd.Timestamp) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "reference_date": reference_date.date().isoformat(),
        "method": (
            "Observed 20th, 40th, 60th, and 80th percentile cutpoints; duplicate "
            "cutpoints are collapsed and values equal to a boundary remain in "
            "the lower value band. Identical raw values always receive the same "
            "score, so band sizes may differ."
        ),
        "directions": {
            "Recency": "Lower values score higher.",
            "Frequency": "Higher values score higher.",
            "Monetary": "Higher values score higher.",
        },
        "metrics": {},
    }
    for metric, score in [
        ("Recency", "R_Score"),
        ("Frequency", "F_Score"),
        ("Monetary", "M_Score"),
    ]:
        bands = []
        for score_value in range(1, 6):
            values = frame.loc[frame[score].eq(score_value), metric]
            bands.append(
                {
                    "score": score_value,
                    "minimum": json_value(values.min()),
                    "maximum": json_value(values.max()),
                    "customer_count": int(values.count()),
                }
            )
        payload["metrics"][metric] = bands
    return payload


def segment_summary(frame: pd.DataFrame) -> pd.DataFrame:
    summary = frame.groupby("Segment", observed=True).agg(
        CustomerCount=("CustomerID", "nunique"),
        Revenue=("Monetary", "sum"),
        Orders=("Frequency", "sum"),
        Units=("UnitsPurchased", "sum"),
        AverageRevenuePerCustomer=("Monetary", "mean"),
        AverageOrdersPerCustomer=("Frequency", "mean"),
        AverageRecency=("Recency", "mean"),
        MedianRecency=("Recency", "median"),
        AverageMonetary=("Monetary", "mean"),
        MedianMonetary=("Monetary", "median"),
        AverageFrequency=("Frequency", "mean"),
        MedianFrequency=("Frequency", "median"),
    ).reset_index()
    summary["CustomerShare"] = summary["CustomerCount"] / len(frame)
    summary["RevenueShare"] = summary["Revenue"] / frame["Monetary"].sum()
    summary["KnownCustomerRevenueContribution"] = summary["RevenueShare"]
    summary["OrderShare"] = summary["Orders"] / frame["Frequency"].sum()
    summary["Segment"] = pd.Categorical(
        summary["Segment"], categories=SEGMENT_ORDER, ordered=True
    )
    return summary.sort_values("Segment").reset_index(drop=True)


def create_figures(summary: pd.DataFrame) -> list[str]:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid")
    labels = summary["Segment"].astype("object")
    created = []

    def save(name: str) -> None:
        path = FIGURE_DIR / name
        plt.tight_layout()
        plt.savefig(path, dpi=160, bbox_inches="tight")
        plt.close()
        created.append(str(path.relative_to(PROJECT_ROOT)).replace("\\", "/"))

    plt.figure(figsize=(10, 5.4))
    plt.barh(labels[::-1], summary["CustomerCount"][::-1], color="#3b7f6d")
    plt.title("RFM Customer Count by Segment")
    plt.xlabel("Customers")
    save("rfm_customer_count_by_segment.png")

    plt.figure(figsize=(10, 5.4))
    plt.barh(labels[::-1], summary["RevenueShare"][::-1] * 100, color="#4c78a8")
    plt.title("Known-Customer Revenue Share by RFM Segment")
    plt.xlabel("Revenue share (%)")
    save("rfm_revenue_share_by_segment.png")

    figure, axes = plt.subplots(1, 3, figsize=(15, 5.4))
    measures = [
        ("AverageRecency", "Recency (days)", "#c04b50"),
        ("AverageFrequency", "Frequency (orders)", "#aa6f39"),
        ("AverageMonetary", "Monetary", "#735290"),
    ]
    for axis, (column, title, color) in zip(axes, measures):
        axis.barh(labels[::-1], summary[column][::-1], color=color)
        axis.set_title(title)
        axis.set_xlabel("Average")
    figure.suptitle("Average RFM Measures by Segment", y=1.02)
    save("rfm_average_measures_by_segment.png")
    return created


def validate(frame: pd.DataFrame, summary: pd.DataFrame, governed: dict[str, Any]) -> list[dict[str, Any]]:
    expected = {
        "Customer count": int(governed["CustomerCount"]),
        "Revenue": float(governed["Revenue"]),
        "Orders": int(governed["OrderCount"]),
        "Units": int(governed["Units"]),
    }
    actual = {
        "Customer count": int(summary["CustomerCount"].sum()),
        "Revenue": float(summary["Revenue"].sum()),
        "Orders": int(summary["Orders"].sum()),
        "Units": int(summary["Units"].sum()),
    }
    checks = []
    for metric in expected:
        tolerance = 0.0001 if metric == "Revenue" else 0
        difference = actual[metric] - expected[metric]
        checks.append(
            {
                "check": f"Segment {metric.lower()} reconciles to governed SQL",
                "actual": actual[metric],
                "expected": expected[metric],
                "difference": difference,
                "status": "PASS" if abs(difference) <= tolerance else "FAIL",
            }
        )
    structural = {
        "Expected approved customer population": len(frame) == EXPECTED_CUSTOMERS,
        "Expected approved known-customer revenue": abs(frame["Monetary"].sum() - EXPECTED_REVENUE) <= 0.0001,
        "One row per customer": frame["CustomerID"].is_unique,
        "Every customer has one named segment": frame["Segment"].isin(SEGMENT_ORDER).all(),
        "No null segments": frame["Segment"].notna().all(),
        "All RFM scores are 1-5": frame[["R_Score", "F_Score", "M_Score"]].isin(range(1, 6)).all().all(),
    }
    for name, passed in structural.items():
        checks.append(
            {
                "check": name,
                "actual": bool(passed),
                "expected": True,
                "difference": None,
                "status": "PASS" if passed else "FAIL",
            }
        )
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server", default="localhost")
    parser.add_argument("--driver", default="ODBC Driver 18 for SQL Server")
    args = parser.parse_args()

    connection = connect_sql(args.server, args.driver)
    try:
        customers, governed = load_customer_rfm(connection)
    finally:
        connection.close()

    frame, reference_date = build_rfm(customers, governed["MaximumInvoiceDate"])
    summary = segment_summary(frame)
    boundaries = score_boundaries(frame, reference_date)
    checks = validate(frame, summary, governed)
    figures = create_figures(summary)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_columns = [
        "CustomerID", "Recency", "Frequency", "Monetary", "R_Score",
        "F_Score", "M_Score", "RFM_Code", "RFM_Total", "Segment",
        "FirstPurchaseDate", "LastPurchaseDate", "UnitsPurchased",
        "ActiveLifespanDays", "AverageOrderValue",
    ]
    export = frame[output_columns].sort_values("CustomerID").copy()
    export["FirstPurchaseDate"] = export["FirstPurchaseDate"].dt.strftime("%Y-%m-%d %H:%M:%S")
    export["LastPurchaseDate"] = export["LastPurchaseDate"].dt.strftime("%Y-%m-%d %H:%M:%S")
    export.to_csv(
        OUTPUT_DIR / "rfm_customer_segments.csv",
        index=False,
        float_format="%.12g",
    )
    summary.to_csv(
        OUTPUT_DIR / "rfm_segment_summary.csv",
        index=False,
        float_format="%.12g",
    )
    (OUTPUT_DIR / "rfm_score_boundaries.json").write_text(
        json.dumps(boundaries, indent=2) + "\n", encoding="utf-8"
    )
    validation_payload = {
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
        "reference_date": reference_date.date().isoformat(),
        "checks": checks,
        "figures": figures,
    }
    (OUTPUT_DIR / "rfm_validation.json").write_text(
        json.dumps(validation_payload, indent=2, default=json_value) + "\n",
        encoding="utf-8",
    )
    print(f"Reference date: {reference_date.date().isoformat()}")
    print(f"Customers: {len(frame):,}")
    print(summary.to_string(index=False))
    print(f"Validation: {validation_payload['status']}")
    return 0 if validation_payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
