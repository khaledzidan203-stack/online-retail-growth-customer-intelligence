"""Create concise Checkpoint 4 exports from governed SQL analytics views."""

from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

import pyodbc


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE = "OnlineRetailAnalytics"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
VIEW_SCRIPTS = [
    PROJECT_ROOT / "sql" / "analysis" / "100_kpi_overview.sql",
    PROJECT_ROOT / "sql" / "analysis" / "110_time_analysis.sql",
    PROJECT_ROOT / "sql" / "analysis" / "120_product_analysis.sql",
    PROJECT_ROOT / "sql" / "analysis" / "130_customer_analysis.sql",
    PROJECT_ROOT / "sql" / "analysis" / "140_country_analysis.sql",
    PROJECT_ROOT / "sql" / "analysis" / "150_cancellation_analysis.sql",
]
VALIDATION_SCRIPT = (
    PROJECT_ROOT / "sql" / "validation" / "190_validate_checkpoint4.sql"
)
GO_PATTERN = re.compile(r"^\s*GO\s*(?:--.*)?$", re.IGNORECASE | re.MULTILINE)

EXPORTS = {
    "checkpoint4_kpi_overview.csv": (
        "SELECT * FROM analytics.vw_KPI_Overview;"
    ),
    "checkpoint4_monthly_performance.csv": (
        "SELECT * FROM analytics.vw_MonthlyPerformance "
        "ORDER BY PeriodStart;"
    ),
    "checkpoint4_time_performance.csv": (
        "SELECT * FROM analytics.vw_TimePerformance "
        "ORDER BY PeriodType, PeriodKey;"
    ),
    "checkpoint4_product_top.csv": (
        "SELECT TOP (100) * FROM analytics.vw_ProductPerformance "
        "WHERE SalesRevenue > 0 ORDER BY RevenueRank;"
    ),
    "checkpoint4_customer_top.csv": (
        "SELECT TOP (100) * FROM analytics.vw_CustomerPerformance "
        "ORDER BY RevenueRank;"
    ),
    "checkpoint4_country_performance.csv": (
        "SELECT * FROM analytics.vw_CountryPerformance "
        "ORDER BY RevenueRank;"
    ),
    "checkpoint4_cancellation_summary.csv": (
        "SELECT * FROM analytics.vw_CancellationPerformance "
        "ORDER BY PeriodStart;"
    ),
}


def connection_string(server: str, driver: str) -> str:
    return (
        f"DRIVER={{{driver}}};SERVER={server};DATABASE={DATABASE};"
        "Trusted_Connection=yes;Encrypt=yes;TrustServerCertificate=yes;"
    )


def split_batches(script: str) -> list[str]:
    return [
        batch.strip()
        for batch in GO_PATTERN.split(script)
        if batch.strip()
    ]


def run_script(
    connection: pyodbc.Connection, path: Path, capture: bool = False
) -> tuple[list[str], list[tuple[Any, ...]]]:
    cursor = connection.cursor()
    columns: list[str] = []
    rows: list[tuple[Any, ...]] = []
    for batch in split_batches(path.read_text(encoding="utf-8")):
        cursor.execute(batch)
        if capture and cursor.description:
            columns = [item[0] for item in cursor.description]
            rows = [tuple(row) for row in cursor.fetchall()]
    connection.commit()
    return columns, rows


def json_safe(value: Any) -> Any:
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def query_records(
    connection: pyodbc.Connection, query: str
) -> list[dict[str, Any]]:
    cursor = connection.cursor().execute(query)
    columns = [item[0] for item in cursor.description]
    return [
        {
            column: json_safe(value)
            for column, value in zip(columns, row)
        }
        for row in cursor.fetchall()
    ]


def write_query_csv(
    connection: pyodbc.Connection, path: Path, query: str
) -> int:
    cursor = connection.cursor().execute(query)
    columns = [item[0] for item in cursor.description]
    rows = cursor.fetchall()
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        for row in rows:
            writer.writerow([json_safe(value) for value in row])
    return len(rows)


CONCENTRATION_QUERIES = {
    "product": """
        SELECT
            CAST(SUM(CASE WHEN RevenueRank <= 10 THEN SalesRevenue ELSE 0 END)
                / SUM(SalesRevenue) AS DECIMAL(28,10)) AS Top10Share,
            CAST(SUM(CASE WHEN RevenueRank <= 20 THEN SalesRevenue ELSE 0 END)
                / SUM(SalesRevenue) AS DECIMAL(28,10)) AS Top20Share,
            CAST(SUM(CASE WHEN RevenueRank <= 100 THEN SalesRevenue ELSE 0 END)
                / SUM(SalesRevenue) AS DECIMAL(28,10)) AS Top100Share,
            MIN(CASE WHEN CumulativeRevenueShare >= 0.50
                THEN RevenueRank END) AS EntitiesTo50Percent,
            MIN(CASE WHEN CumulativeRevenueShare >= 0.80
                THEN RevenueRank END) AS EntitiesTo80Percent,
            MIN(CASE WHEN CumulativeRevenueShare >= 0.90
                THEN RevenueRank END) AS EntitiesTo90Percent
        FROM analytics.vw_ProductPerformance
        WHERE SalesRevenue > 0;
    """,
    "customer": """
        SELECT
            CAST(SUM(CASE WHEN RevenueRank <= 10 THEN SalesRevenue ELSE 0 END)
                / SUM(SalesRevenue) AS DECIMAL(28,10)) AS Top10Share,
            CAST(SUM(CASE WHEN RevenueRank <= 20 THEN SalesRevenue ELSE 0 END)
                / SUM(SalesRevenue) AS DECIMAL(28,10)) AS Top20Share,
            CAST(SUM(CASE WHEN RevenueRank <= 100 THEN SalesRevenue ELSE 0 END)
                / SUM(SalesRevenue) AS DECIMAL(28,10)) AS Top100Share,
            MIN(CASE WHEN CumulativeRevenueShare >= 0.50
                THEN RevenueRank END) AS EntitiesTo50Percent,
            MIN(CASE WHEN CumulativeRevenueShare >= 0.80
                THEN RevenueRank END) AS EntitiesTo80Percent,
            MIN(CASE WHEN CumulativeRevenueShare >= 0.90
                THEN RevenueRank END) AS EntitiesTo90Percent
        FROM analytics.vw_CustomerPerformance;
    """,
    "country": """
        SELECT
            CAST(SUM(CASE WHEN RevenueRank <= 10 THEN SalesRevenue ELSE 0 END)
                / SUM(SalesRevenue) AS DECIMAL(28,10)) AS Top10Share,
            CAST(SUM(CASE WHEN RevenueRank <= 20 THEN SalesRevenue ELSE 0 END)
                / SUM(SalesRevenue) AS DECIMAL(28,10)) AS Top20Share,
            CAST(SUM(CASE WHEN RevenueRank <= 43 THEN SalesRevenue ELSE 0 END)
                / SUM(SalesRevenue) AS DECIMAL(28,10)) AS AllMarketShare,
            MIN(CASE WHEN CumulativeRevenueShare >= 0.50
                THEN RevenueRank END) AS EntitiesTo50Percent,
            MIN(CASE WHEN CumulativeRevenueShare >= 0.80
                THEN RevenueRank END) AS EntitiesTo80Percent,
            MIN(CASE WHEN CumulativeRevenueShare >= 0.90
                THEN RevenueRank END) AS EntitiesTo90Percent
        FROM analytics.vw_CountryPerformance;
    """,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server", default="localhost")
    parser.add_argument("--driver", default="ODBC Driver 18 for SQL Server")
    args = parser.parse_args()

    connection = pyodbc.connect(
        connection_string(args.server, args.driver), autocommit=False
    )
    try:
        for script in VIEW_SCRIPTS:
            run_script(connection, script)

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        export_counts = {
            filename: write_query_csv(
                connection, OUTPUT_DIR / filename, query
            )
            for filename, query in EXPORTS.items()
        }

        validation_columns, validation_rows = run_script(
            connection, VALIDATION_SCRIPT, capture=True
        )
        validations = [
            {
                column: json_safe(value)
                for column, value in zip(validation_columns, row)
            }
            for row in validation_rows
        ]
        failed = [
            item["Metric"]
            for item in validations
            if item["ValidationStatus"] == "FAIL"
        ]

        summary = {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "server": args.server,
            "database": DATABASE,
            "validation_status": "PASS" if not failed else "FAIL",
            "failed_validations": failed,
            "exports": export_counts,
            "kpi_overview": query_records(
                connection,
                "SELECT * FROM analytics.vw_KPI_Overview;",
            )[0],
            "concentration": {
                name: query_records(connection, query)[0]
                for name, query in CONCENTRATION_QUERIES.items()
            },
            "top_products": query_records(
                connection,
                """
                SELECT N'Revenue' AS Ranking, StockCode,
                    RepresentativeDescription, SalesRevenue AS MetricValue
                FROM (SELECT TOP (1) * FROM analytics.vw_ProductPerformance
                      WHERE SalesRevenue > 0 ORDER BY RevenueRank) AS ranked
                UNION ALL
                SELECT N'Units', StockCode, RepresentativeDescription,
                    CONVERT(DECIMAL(28,8), UnitsSold)
                FROM (SELECT TOP (1) * FROM analytics.vw_ProductPerformance
                      WHERE SalesRevenue > 0 ORDER BY UnitsRank) AS ranked
                UNION ALL
                SELECT N'Orders', StockCode, RepresentativeDescription,
                    CONVERT(DECIMAL(28,8), Orders)
                FROM (SELECT TOP (1) * FROM analytics.vw_ProductPerformance
                      WHERE SalesRevenue > 0 ORDER BY OrdersRank) AS ranked
                UNION ALL
                SELECT N'Known Customers', StockCode,
                    RepresentativeDescription,
                    CONVERT(DECIMAL(28,8), KnownCustomers)
                FROM (SELECT TOP (1) * FROM analytics.vw_ProductPerformance
                      WHERE SalesRevenue > 0
                      ORDER BY KnownCustomerRank) AS ranked;
                """,
            ),
            "yearly_performance": query_records(
                connection,
                "SELECT * FROM analytics.vw_TimePerformance "
                "WHERE PeriodType = N'YEAR' ORDER BY PeriodKey;",
            ),
            "like_for_like_2010_2011": query_records(
                connection,
                """
                SELECT
                    YEAR(InvoiceDate) AS CalendarYear,
                    SUM(CASE WHEN IsSalesEligible = 1
                        THEN LineAmount ELSE 0 END) AS SalesRevenue,
                    COUNT(DISTINCT CASE WHEN IsSalesEligible = 1
                        THEN Invoice END) AS Orders,
                    SUM(CASE WHEN IsSalesEligible = 1
                        THEN CONVERT(BIGINT, Quantity) ELSE 0 END) AS Units,
                    SUM(CASE WHEN IsCancellationEligible = 1
                        THEN ABS(LineAmount) ELSE 0 END) AS CancellationValue
                FROM analytics.FactTransaction
                WHERE
                    (InvoiceDate >= '20100101' AND InvoiceDate < '20101210')
                    OR
                    (InvoiceDate >= '20110101' AND InvoiceDate < '20111210')
                GROUP BY YEAR(InvoiceDate)
                ORDER BY CalendarYear;
                """,
            ),
            "time_headlines": {
                "top_month": query_records(
                    connection,
                    "SELECT TOP (1) * FROM analytics.vw_MonthlyPerformance "
                    "ORDER BY SalesRevenue DESC, PeriodStart;",
                )[0],
                "top_quarter": query_records(
                    connection,
                    "SELECT TOP (1) * FROM analytics.vw_TimePerformance "
                    "WHERE PeriodType=N'QUARTER' "
                    "ORDER BY SalesRevenue DESC, PeriodKey;",
                )[0],
                "top_day_of_week": query_records(
                    connection,
                    "SELECT TOP (1) * FROM analytics.vw_TimePerformance "
                    "WHERE PeriodType=N'DAY_OF_WEEK' "
                    "ORDER BY SalesRevenue DESC, PeriodKey;",
                )[0],
                "top_hour": query_records(
                    connection,
                    "SELECT TOP (1) * FROM analytics.vw_TimePerformance "
                    "WHERE PeriodType=N'HOUR_OF_DAY' "
                    "ORDER BY SalesRevenue DESC, PeriodKey;",
                )[0],
            },
            "market_headlines": {
                "uk_vs_non_uk": query_records(
                    connection,
                    """
                    SELECT
                        CASE WHEN Country = N'United Kingdom'
                            THEN N'United Kingdom' ELSE N'Non-UK' END AS Market,
                        SUM(SalesRevenue) AS SalesRevenue,
                        CAST(SUM(SalesRevenue)
                            / SUM(SUM(SalesRevenue)) OVER ()
                            AS DECIMAL(28,10)) AS RevenueShare
                    FROM analytics.vw_CountryPerformance
                    GROUP BY CASE WHEN Country = N'United Kingdom'
                        THEN N'United Kingdom' ELSE N'Non-UK' END;
                    """,
                ),
                "top_revenue": query_records(
                    connection,
                    "SELECT TOP (1) * FROM analytics.vw_CountryPerformance "
                    "ORDER BY SalesRevenue DESC, Country;",
                )[0],
                "top_aov_min_100_orders": query_records(
                    connection,
                    "SELECT TOP (1) * FROM analytics.vw_CountryPerformance "
                    "WHERE Orders >= 100 "
                    "ORDER BY AverageOrderValue DESC, Country;",
                )[0],
                "top_known_customers": query_records(
                    connection,
                    "SELECT TOP (1) * FROM analytics.vw_CountryPerformance "
                    "ORDER BY KnownCustomers DESC, Country;",
                )[0],
                "top_cancellation_rate_min_100_orders": query_records(
                    connection,
                    "SELECT TOP (1) * FROM analytics.vw_CountryPerformance "
                    "WHERE MeetsCancellationRateMinimumBase = 1 "
                    "ORDER BY CancellationValueRate DESC, Country;",
                )[0],
            },
            "cancellation_headlines": {
                "top_product": query_records(
                    connection,
                    "SELECT TOP (1) StockCode, RepresentativeDescription, "
                    "CancellationValue, CancellationUnits "
                    "FROM analytics.vw_ProductPerformance "
                    "ORDER BY CancellationValue DESC, StockCode;",
                )[0],
                "top_customer": query_records(
                    connection,
                    """
                    SELECT TOP (1)
                        customer.CustomerID,
                        SUM(ABS(fact.LineAmount)) AS CancellationValue
                    FROM analytics.FactTransaction AS fact
                    INNER JOIN analytics.DimCustomer AS customer
                        ON customer.CustomerKey = fact.CustomerKey
                    WHERE fact.IsCancellationEligible = 1
                    GROUP BY customer.CustomerID
                    ORDER BY CancellationValue DESC, customer.CustomerID;
                    """,
                )[0],
                "top_country": query_records(
                    connection,
                    "SELECT TOP (1) Country, CancellationValue "
                    "FROM analytics.vw_CountryPerformance "
                    "ORDER BY CancellationValue DESC, Country;",
                )[0],
                "top_month": query_records(
                    connection,
                    "SELECT TOP (1) * "
                    "FROM analytics.vw_CancellationPerformance "
                    "ORDER BY CancellationValue DESC, PeriodStart;",
                )[0],
            },
            "validations": validations,
        }
    finally:
        connection.close()

    output_path = OUTPUT_DIR / "checkpoint4_sql_analysis.json"
    output_path.write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Overall: {summary['validation_status']}")
    print(f"Exports: {len(export_counts)}")
    print(f"Output: {output_path.resolve()}")
    return 0 if summary["validation_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
