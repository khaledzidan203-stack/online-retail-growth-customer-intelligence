"""Shared SQL access, validation, and distribution utilities for analytics."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

import pandas as pd
import pyodbc


DATABASE = "OnlineRetailAnalytics"


def connect_sql(
    server: str = "localhost",
    driver: str = "ODBC Driver 18 for SQL Server",
) -> pyodbc.Connection:
    connection_string = (
        f"DRIVER={{{driver}}};SERVER={server};DATABASE={DATABASE};"
        "Trusted_Connection=yes;Encrypt=yes;TrustServerCertificate=yes;"
    )
    return pyodbc.connect(connection_string)


def query_frame(
    connection: pyodbc.Connection, query: str
) -> pd.DataFrame:
    cursor = connection.cursor().execute(query)
    columns = [item[0] for item in cursor.description]
    return pd.DataFrame.from_records(cursor.fetchall(), columns=columns)


def numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="raise")


def distribution_record(
    grain: str, metric: str, values: pd.Series
) -> dict[str, Any]:
    clean = numeric(values).dropna().astype(float)
    quantiles = clean.quantile(
        [0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
    )
    return {
        "grain": grain,
        "metric": metric,
        "count": int(clean.count()),
        "mean": float(clean.mean()),
        "std": float(clean.std(ddof=1)),
        "min": float(clean.min()),
        "p25": float(quantiles.loc[0.25]),
        "median": float(quantiles.loc[0.50]),
        "p75": float(quantiles.loc[0.75]),
        "p90": float(quantiles.loc[0.90]),
        "p95": float(quantiles.loc[0.95]),
        "p99": float(quantiles.loc[0.99]),
        "max": float(clean.max()),
    }


def validation_records(
    actual: dict[str, float | int],
    expected: dict[str, float | int],
) -> list[dict[str, Any]]:
    rows = []
    for metric, expected_value in expected.items():
        actual_value = actual[metric]
        tolerance = 0.0001 if isinstance(expected_value, float) else 0
        difference = float(actual_value) - float(expected_value)
        rows.append(
            {
                "metric": metric,
                "python_actual": actual_value,
                "sql_expected": expected_value,
                "difference": difference,
                "status": (
                    "PASS"
                    if abs(difference) <= tolerance
                    else "FAIL"
                ),
            }
        )
    return rows


def json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, (date, datetime, pd.Timestamp)):
        return value.isoformat()
    if hasattr(value, "item"):
        return value.item()
    return value
