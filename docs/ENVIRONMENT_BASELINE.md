# Environment Baseline

## Python

The repository requirements currently pin:

- pandas 3.0.5
- openpyxl 3.1.5
- pyarrow 25.0.1
- pyodbc 5.3.0
- matplotlib 3.11.1
- numpy 2.5.2

The project documentation targets a Python 3.13-compatible environment.

## SQL Server

- Database: `OnlineRetailAnalytics`
- SQL Server development instance required for full reproduction
- Microsoft ODBC Driver 18 recommended by the main run guide
- Windows authentication used by the documented workflow

## Power BI

The repository includes a PBIP project with PBIR and TMDL source.

A compatible Power BI Desktop version and local SQL access are required for a fresh refresh.

## Excel

Management workbooks are generated with Python/openpyxl from governed SQL queries.

## GitHub CI

The public CI is intentionally runtime-light:

- no SQL Server service is provisioned;
- no Power BI Desktop runtime is available;
- no raw UCI workbook is downloaded.

CI therefore validates committed source/evidence contracts rather than claiming a fresh end-to-end business-data refresh.
