"""Load the governed canonical Parquet file into the SQL Server star schema."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq
import pyodbc


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PARQUET_SOURCE = (
    PROJECT_ROOT / "data" / "interim" / "canonical_transactions.parquet"
)
OUTPUT_PATH = PROJECT_ROOT / "outputs" / "checkpoint3_sql_reconciliation.json"
DATABASE = "OnlineRetailAnalytics"
SQL_SCRIPTS = {
    "database": PROJECT_ROOT / "sql" / "ddl" / "001_create_database.sql",
    "schemas": PROJECT_ROOT / "sql" / "ddl" / "002_create_schemas.sql",
    "raw": PROJECT_ROOT / "sql" / "raw" / "010_create_raw_transaction.sql",
    "staging": (
        PROJECT_ROOT
        / "sql"
        / "staging"
        / "020_create_staging_transaction.sql"
    ),
    "dimensions": (
        PROJECT_ROOT / "sql" / "analytics" / "030_create_dimensions.sql"
    ),
    "fact": (
        PROJECT_ROOT
        / "sql"
        / "analytics"
        / "040_create_fact_transaction.sql"
    ),
    "validation": (
        PROJECT_ROOT / "sql" / "validation" / "090_validate_checkpoint3.sql"
    ),
}

LOAD_COLUMNS = [
    "SourceSheet",
    "SourceRowNumber",
    "InvoiceRaw",
    "Invoice",
    "StockCodeRaw",
    "StockCode",
    "DescriptionRaw",
    "Description",
    "Quantity",
    "InvoiceDate",
    "Price",
    "CustomerIDRaw",
    "CustomerID",
    "CountryRaw",
    "Country",
    "LineAmount",
    "IsExactDuplicateAfterFirst",
    "IsInExactDuplicateGroup",
    "ExactDuplicateGroupSize",
    "ItemClass",
    "TransactionClass",
    "DQReviewReason",
    "IsKnownCustomer",
    "IsCancellationInvoice",
    "IsMerchandise",
    "IsSalesEligible",
    "IsCustomerAnalyticsEligible",
    "IsCancellationEligible",
    "IsZeroPrice",
    "IsNegativePrice",
]
DECIMAL_QUANTUM = {
    "Price": Decimal("0.00000001"),
    "CustomerIDRaw": Decimal("0.0001"),
    "LineAmount": Decimal("0.00000001"),
}
GO_PATTERN = re.compile(r"^\s*GO\s*(?:--.*)?$", re.IGNORECASE | re.MULTILINE)


def connection_string(
    server: str, database: str, driver: str
) -> str:
    return (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        "Trusted_Connection=yes;"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
    )


def split_batches(script: str) -> list[str]:
    return [
        batch.strip()
        for batch in GO_PATTERN.split(script)
        if batch.strip()
    ]


def run_script(
    connection: pyodbc.Connection, path: Path, capture_rows: bool = False
) -> list[tuple[Any, ...]]:
    cursor = connection.cursor()
    captured: list[tuple[Any, ...]] = []
    for batch in split_batches(path.read_text(encoding="utf-8")):
        cursor.execute(batch)
        if capture_rows and cursor.description:
            captured = cursor.fetchall()
    connection.commit()
    return captured


def prepare_row(values: tuple[Any, ...]) -> tuple[Any, ...]:
    prepared = []
    for column, value in zip(LOAD_COLUMNS, values):
        if value is not None and column in DECIMAL_QUANTUM:
            prepared.append(
                Decimal(str(value)).quantize(DECIMAL_QUANTUM[column])
            )
        else:
            prepared.append(value)
    return tuple(prepared)


def load_raw(
    connection: pyodbc.Connection,
    parquet_path: Path,
    batch_size: int,
) -> int:
    parquet = pq.ParquetFile(parquet_path)
    missing = sorted(set(LOAD_COLUMNS) - set(parquet.schema.names))
    if missing:
        raise ValueError(f"Parquet source is missing columns: {missing}")

    column_sql = ", ".join(f"[{column}]" for column in LOAD_COLUMNS)
    placeholders = ", ".join("?" for _ in LOAD_COLUMNS)
    insert_sql = (
        "INSERT INTO raw.OnlineRetailTransaction "
        f"({column_sql}) VALUES ({placeholders})"
    )
    cursor = connection.cursor()
    cursor.execute("TRUNCATE TABLE raw.OnlineRetailTransaction;")
    connection.commit()
    cursor.fast_executemany = True

    loaded = 0
    for batch in parquet.iter_batches(
        batch_size=batch_size, columns=LOAD_COLUMNS
    ):
        data = batch.to_pydict()
        rows = [
            prepare_row(values)
            for values in zip(*(data[column] for column in LOAD_COLUMNS))
        ]
        cursor.executemany(insert_sql, rows)
        connection.commit()
        loaded += len(rows)
        if loaded % 100_000 < len(rows):
            print(f"Loaded raw rows: {loaded:,}")
    return loaded


def decimal_json(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, Decimal):
        if value == value.to_integral_value():
            return int(value)
        return format(value.normalize(), "f")
    return value


def validation_payload(
    rows: list[tuple[Any, ...]],
    server_argument: str,
    server_details: tuple[Any, ...],
    loaded_rows: int,
) -> dict[str, Any]:
    validations = [
        {
            "metric": row[0],
            "actual": decimal_json(row[1]),
            "expected": decimal_json(row[2]),
            "status": row[3],
        }
        for row in rows
    ]
    failed = [
        item["metric"] for item in validations if item["status"] == "FAIL"
    ]
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "connection": {
            "server_argument": server_argument,
            "server_name": server_details[0],
            "product_version": server_details[1],
            "windows_login": server_details[2],
            "database": DATABASE,
            "authentication": "Windows Authentication",
        },
        "source": {
            "path": "data/interim/canonical_transactions.parquet",
            "loaded_rows": loaded_rows,
        },
        "validations": validations,
        "failed_metrics": failed,
        "overall_status": "PASS" if not failed else "FAIL",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server", default="localhost")
    parser.add_argument("--driver", default="ODBC Driver 18 for SQL Server")
    parser.add_argument("--parquet", type=Path, default=PARQUET_SOURCE)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--batch-size", type=int, default=5_000)
    args = parser.parse_args()

    if not args.parquet.is_file():
        raise FileNotFoundError(f"Canonical Parquet not found: {args.parquet}")
    missing_scripts = [
        str(path) for path in SQL_SCRIPTS.values() if not path.is_file()
    ]
    if missing_scripts:
        raise FileNotFoundError(f"Missing SQL scripts: {missing_scripts}")

    master_connection = pyodbc.connect(
        connection_string(args.server, "master", args.driver),
        autocommit=True,
    )
    try:
        run_script(master_connection, SQL_SCRIPTS["database"])
    finally:
        master_connection.close()

    connection = pyodbc.connect(
        connection_string(args.server, DATABASE, args.driver),
        autocommit=False,
    )
    try:
        run_script(connection, SQL_SCRIPTS["schemas"])
        run_script(connection, SQL_SCRIPTS["raw"])
        loaded_rows = load_raw(
            connection, args.parquet.resolve(), args.batch_size
        )
        if loaded_rows != 1_044_848:
            raise ValueError(
                f"Loaded {loaded_rows:,} rows; expected 1,044,848"
            )
        run_script(connection, SQL_SCRIPTS["staging"])
        run_script(connection, SQL_SCRIPTS["dimensions"])
        run_script(connection, SQL_SCRIPTS["fact"])
        validation_rows = run_script(
            connection, SQL_SCRIPTS["validation"], capture_rows=True
        )
        server_details = connection.cursor().execute(
            "SELECT "
            "CAST(SERVERPROPERTY('ServerName') AS nvarchar(128)), "
            "CAST(SERVERPROPERTY('ProductVersion') AS nvarchar(128)), "
            "SUSER_SNAME();"
        ).fetchone()
    finally:
        connection.close()

    payload = validation_payload(
        validation_rows,
        args.server,
        tuple(server_details),
        loaded_rows,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    review_count = sum(
        item["status"] == "REVIEW" for item in payload["validations"]
    )
    print(f"Overall: {payload['overall_status']}")
    print(f"Loaded rows: {loaded_rows:,}")
    print(f"Review-only metrics: {review_count}")
    print(f"Output: {args.output.resolve()}")
    return 0 if payload["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
