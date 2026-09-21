"""Publish validated Python customer analytics outputs to SQL Server."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
import pyodbc


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "outputs"
DATABASE = "OnlineRetailAnalytics"
DDL_PATH = PROJECT_ROOT / "sql" / "analytics" / "250_create_customer_analytics.sql"
VALIDATION_PATH = PROJECT_ROOT / "sql" / "validation" / "290_validate_checkpoint6a.sql"
RECONCILIATION_PATH = OUTPUT_DIR / "checkpoint6a_customer_analytics_sql.json"
SOURCE_PATHS = {
    "rfm": OUTPUT_DIR / "rfm_customer_segments.csv",
    "rfm_boundaries": OUTPUT_DIR / "rfm_score_boundaries.json",
    "cohort_retention": OUTPUT_DIR / "cohort_customer_retention.csv",
    "cohort_revenue": OUTPUT_DIR / "cohort_revenue.csv",
    "repeat": OUTPUT_DIR / "customer_repeat_timing.csv",
}
GO_PATTERN = re.compile(r"^\s*GO\s*(?:--.*)?$", re.IGNORECASE | re.MULTILINE)


def connection_string(server: str, driver: str) -> str:
    return (
        f"DRIVER={{{driver}}};SERVER={server};DATABASE={DATABASE};"
        "Trusted_Connection=yes;Encrypt=yes;TrustServerCertificate=yes;"
    )


def split_batches(script: str) -> list[str]:
    return [batch.strip() for batch in GO_PATTERN.split(script) if batch.strip()]


def run_script(
    connection: pyodbc.Connection,
    path: Path,
    capture_rows: bool = False,
) -> list[tuple[Any, ...]]:
    captured: list[tuple[Any, ...]] = []
    cursor = connection.cursor()
    for batch in split_batches(path.read_text(encoding="utf-8")):
        cursor.execute(batch)
        while True:
            if capture_rows and cursor.description:
                captured = [tuple(row) for row in cursor.fetchall()]
            if not cursor.nextset():
                break
    connection.commit()
    return captured


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def customer_id(value: Any) -> str:
    if pd.isna(value):
        raise ValueError("CustomerID cannot be null")
    if isinstance(value, str):
        return value.strip()
    return str(int(value))


def decimal_value(value: Any, scale: int = 8) -> Decimal:
    quantum = Decimal(1).scaleb(-scale)
    return Decimal(str(value)).quantize(quantum)


def optional_datetime(value: Any) -> datetime | None:
    if pd.isna(value):
        return None
    return pd.Timestamp(value).to_pydatetime()


def read_sources() -> dict[str, Any]:
    missing = [str(path) for path in SOURCE_PATHS.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing governed outputs: {missing}")
    frames = {
        "rfm": pd.read_csv(SOURCE_PATHS["rfm"]),
        "retention": pd.read_csv(SOURCE_PATHS["cohort_retention"]),
        "revenue": pd.read_csv(SOURCE_PATHS["cohort_revenue"]),
        "repeat": pd.read_csv(SOURCE_PATHS["repeat"]),
    }
    boundaries = json.loads(SOURCE_PATHS["rfm_boundaries"].read_text(encoding="utf-8"))
    return {**frames, "reference_date": pd.Timestamp(boundaries["reference_date"])}


def preflight(sources: dict[str, Any]) -> None:
    rfm = sources["rfm"]
    repeat = sources["repeat"]
    retention = sources["retention"]
    revenue = sources["revenue"]
    rfm_ids = {customer_id(value) for value in rfm["CustomerID"]}
    repeat_ids = {customer_id(value) for value in repeat["CustomerID"]}
    if len(rfm) != 5_852 or len(rfm_ids) != 5_852:
        raise ValueError("RFM source must contain 5,852 unique customers")
    if len(repeat) != 5_852 or len(repeat_ids) != 5_852:
        raise ValueError("Repeat source must contain 5,852 unique customers")
    if rfm_ids != repeat_ids:
        raise ValueError("RFM and repeat customer populations differ")
    if abs(float(rfm["Monetary"].sum()) - 17_125_672.047) > 0.0001:
        raise ValueError("RFM monetary source does not reconcile")
    if int(rfm["Frequency"].sum()) != 36_597:
        raise ValueError("RFM frequency source does not reconcile")
    if int(repeat["HasRepeatPurchase"].sum()) != 4_234:
        raise ValueError("Repeat source does not reconcile")
    retention_grain = set(zip(retention["AcquisitionCohort"], retention["CohortIndex"]))
    revenue_grain = set(zip(revenue["AcquisitionCohort"], revenue["CohortIndex"]))
    if len(retention) != 325 or len(retention_grain) != 325:
        raise ValueError("Retention source grain is not unique or complete")
    if len(revenue) != 325 or len(revenue_grain) != 325:
        raise ValueError("Revenue source grain is not unique or complete")
    if retention_grain != revenue_grain:
        raise ValueError("Retention and revenue grains differ")
    if abs(float(revenue["Revenue"].sum()) - 17_125_672.047) > 0.0001:
        raise ValueError("Cohort revenue source does not reconcile")
    if int(revenue["Orders"].sum()) != 36_597:
        raise ValueError("Cohort order source does not reconcile")


def customer_mapping(connection: pyodbc.Connection) -> dict[str, int]:
    rows = connection.cursor().execute(
        "SELECT CustomerKey, CustomerID FROM analytics.DimCustomer;"
    ).fetchall()
    mapping = {str(row.CustomerID): int(row.CustomerKey) for row in rows}
    if len(mapping) != len(rows):
        raise ValueError("DimCustomer contains duplicate CustomerID mappings")
    if len(mapping) != 5_942:
        raise ValueError(f"DimCustomer contains {len(mapping):,} rows; expected 5,942")
    return mapping


def resolve_customer_keys(
    sources: dict[str, Any], mapping: dict[str, int]
) -> None:
    for name in ["rfm", "repeat"]:
        frame = sources[name]
        frame["CustomerID"] = frame["CustomerID"].map(customer_id)
        frame["CustomerKey"] = frame["CustomerID"].map(mapping)
        missing = frame.loc[frame["CustomerKey"].isna(), "CustomerID"].tolist()
        if missing:
            raise ValueError(f"{name} has unmapped customers: {missing[:10]}")
        frame["CustomerKey"] = frame["CustomerKey"].astype("int64")
    if set(sources["rfm"]["CustomerKey"]) != set(sources["repeat"]["CustomerKey"]):
        raise ValueError("Resolved customer-key populations differ")


def execute_many(
    cursor: pyodbc.Cursor,
    statement: str,
    rows: Iterable[tuple[Any, ...]],
) -> None:
    cursor.fast_executemany = True
    cursor.executemany(statement, list(rows))


def load_tables(connection: pyodbc.Connection, sources: dict[str, Any]) -> None:
    cursor = connection.cursor()
    for table in [
        "analytics.CustomerRFM",
        "analytics.CustomerCohort",
        "analytics.CustomerRepeatBehavior",
        "analytics.CohortRetention",
        "analytics.CohortRevenue",
    ]:
        cursor.execute(f"DELETE FROM {table};")

    rfm = sources["rfm"]
    reference_date = sources["reference_date"].date()
    execute_many(
        cursor,
        """
        INSERT INTO analytics.CustomerRFM
        (CustomerKey, CustomerID, ReferenceDate, Recency, Frequency, Monetary,
         R_Score, F_Score, M_Score, RFM_Code, RFM_Total, Segment,
         FirstPurchaseDate, LastPurchaseDate, UnitsPurchased,
         ActiveLifespanDays, AverageOrderValue)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            (
                int(row.CustomerKey), row.CustomerID, reference_date,
                int(row.Recency), int(row.Frequency), decimal_value(row.Monetary),
                int(row.R_Score), int(row.F_Score), int(row.M_Score),
                str(row.RFM_Code), int(row.RFM_Total), str(row.Segment),
                pd.Timestamp(row.FirstPurchaseDate).to_pydatetime(),
                pd.Timestamp(row.LastPurchaseDate).to_pydatetime(),
                int(row.UnitsPurchased), int(row.ActiveLifespanDays),
                decimal_value(row.AverageOrderValue),
            )
            for row in rfm.itertuples(index=False)
        ),
    )

    repeat = sources["repeat"]
    execute_many(
        cursor,
        """
        INSERT INTO analytics.CustomerCohort
        (CustomerKey, CustomerID, FirstPurchaseDate, AcquisitionCohort,
         IsLeftBoundaryAffected)
        VALUES (?, ?, ?, ?, ?);
        """,
        (
            (
                int(row.CustomerKey), row.CustomerID,
                pd.Timestamp(row.FirstPurchaseDate).to_pydatetime(),
                str(row.AcquisitionCohort),
                str(row.AcquisitionCohort) == "2009-12",
            )
            for row in repeat.itertuples(index=False)
        ),
    )
    execute_many(
        cursor,
        """
        INSERT INTO analytics.CustomerRepeatBehavior
        (CustomerKey, CustomerID, FirstPurchaseDate, SecondPurchaseDate,
         DaysToSecondPurchase, HasRepeatPurchase)
        VALUES (?, ?, ?, ?, ?, ?);
        """,
        (
            (
                int(row.CustomerKey), row.CustomerID,
                pd.Timestamp(row.FirstPurchaseDate).to_pydatetime(),
                optional_datetime(row.SecondPurchaseDate),
                None if pd.isna(row.DaysToSecondPurchase) else int(row.DaysToSecondPurchase),
                bool(row.HasRepeatPurchase),
            )
            for row in repeat.itertuples(index=False)
        ),
    )

    retention = sources["retention"]
    execute_many(
        cursor,
        """
        INSERT INTO analytics.CohortRetention
        (AcquisitionCohort, CohortIndex, ActivityMonth, CohortSize,
         ActiveCustomers, RetentionRate, IsLeftBoundaryCohort,
         IsPartialObservation, ObservationStatus)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            (
                str(row.AcquisitionCohort), int(row.CohortIndex),
                str(row.ActivityMonth), int(row.CohortSize),
                int(row.ActiveCustomers), decimal_value(row.RetentionRate, 12),
                str(row.AcquisitionCohort) == "2009-12",
                bool(row.IsPartialObservation), str(row.ObservationStatus),
            )
            for row in retention.itertuples(index=False)
        ),
    )

    revenue = sources["revenue"]
    execute_many(
        cursor,
        """
        INSERT INTO analytics.CohortRevenue
        (AcquisitionCohort, CohortIndex, ActivityMonth, CohortSize, Revenue,
         RevenuePerOriginalCustomer, Orders, OrdersPerOriginalCustomer,
         IsLeftBoundaryCohort, IsPartialObservation, ObservationStatus)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            (
                str(row.AcquisitionCohort), int(row.CohortIndex),
                str(row.ActivityMonth), int(row.CohortSize),
                decimal_value(row.Revenue),
                decimal_value(row.RevenuePerOriginalCustomer),
                int(row.Orders), decimal_value(row.OrdersPerOriginalCustomer, 12),
                str(row.AcquisitionCohort) == "2009-12",
                bool(row.IsPartialObservation), str(row.ObservationStatus),
            )
            for row in revenue.itertuples(index=False)
        ),
    )
    connection.commit()


def json_scalar(value: Any) -> Any:
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server", default="localhost")
    parser.add_argument("--driver", default="ODBC Driver 18 for SQL Server")
    parser.add_argument("--output", type=Path, default=RECONCILIATION_PATH)
    args = parser.parse_args()

    sources = read_sources()
    preflight(sources)
    connection = pyodbc.connect(connection_string(args.server, args.driver), autocommit=False)
    try:
        mapping = customer_mapping(connection)
        resolve_customer_keys(sources, mapping)
        run_script(connection, DDL_PATH)
        load_tables(connection, sources)
        validation_rows = run_script(connection, VALIDATION_PATH, capture_rows=True)
        server_details = tuple(
            connection.cursor().execute(
                "SELECT CAST(SERVERPROPERTY('ServerName') AS nvarchar(128)), "
                "CAST(SERVERPROPERTY('ProductVersion') AS nvarchar(128)), "
                "SUSER_SNAME();"
            ).fetchone()
        )
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    validations = [
        {
            "metric": row[0],
            "actual": json_scalar(row[1]),
            "expected": json_scalar(row[2]),
            "status": row[3],
        }
        for row in validation_rows
    ]
    failed = [item["metric"] for item in validations if item["status"] != "PASS"]
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "connection": {
            "server_argument": args.server,
            "server_name": server_details[0],
            "product_version": server_details[1],
            "windows_login": server_details[2],
            "database": DATABASE,
            "authentication": "Windows Authentication",
        },
        "publication_method": "Validated Python outputs loaded without SQL model recalculation.",
        "sources": {
            name: {
                "path": str(path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "sha256": file_sha256(path),
            }
            for name, path in SOURCE_PATHS.items()
        },
        "dim_customer_rows": len(mapping),
        "published_customer_rows": len(sources["rfm"]),
        "validations": validations,
        "failed_metrics": failed,
        "overall_status": "PASS" if not failed else "FAIL",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Published customer rows: {len(sources['rfm']):,}")
    print(f"Validation metrics: {len(validations)}")
    print(f"Overall: {payload['overall_status']}")
    print(f"Output: {args.output.resolve()}")
    return 0 if payload["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
