# Python portfolio

Python supports the full pipeline: source profiling, governed canonical processing, SQL loading, exploratory analysis, RFM/cohort processing, reconciliation and management Excel generation.

| Entry point | Purpose |
|---|---|
| [ingestion/profile_raw_dataset.py](ingestion/profile_raw_dataset.py) | Profile the two-sheet UCI workbook and record source quality |
| [cleaning/build_canonical_transactions.py](cleaning/build_canonical_transactions.py) | Normalize/classify transactions using config/item_classification.json; write local canonical Parquet and reconciliation |
| [ingestion/load_sql_server.py](ingestion/load_sql_server.py) | Load raw, staging, dimensions and fact; run foundation SQL checks |
| [analytics/export_sql_analysis.py](analytics/export_sql_analysis.py) | Create business views and export concise SQL analysis evidence |
| [analytics/eda.py](analytics/eda.py) | Explore the governed SQL baseline and create analytical charts |
| [analytics/rfm.py](analytics/rfm.py) | Calculate the validated customer RFM snapshot |
| [analytics/cohort.py](analytics/cohort.py) | Calculate cohort retention/revenue and repeat-purchase outputs |
| [analytics/validation.py](analytics/validation.py) | Shared SQL and reconciliation helpers |
| [ingestion/publish_customer_analytics.py](ingestion/publish_customer_analytics.py) | Publish validated customer outputs to SQL analytical tables |
| [exports/management_export.py](exports/management_export.py) | Generate two Excel workbooks or validate saved analytical cells |
| [exports/sql_queries.py](exports/sql_queries.py) | Governed SQL query definitions for management export |

Follow the [ordered reproduction commands](../README.md#reproduce-the-project). SQL scripts run through the Python orchestrators, which handle SQL Server batch separators.

## Dependencies and access

[requirements.txt](../requirements.txt) contains the six external libraries actually used by the source: pandas, openpyxl, PyArrow, pyodbc, matplotlib and NumPy. Standard-library imports and local helper modules do not need separate packages. Version pins are retained from the completed project.

SQL access uses Windows authentication. Pass your local instance with `--server`; scripts accept `--driver`. The management exporter defaults to ODBC 17, so the README commands explicitly select ODBC 18 for consistency.

Raw data and canonical Parquet remain local. Some generated reconciliation metadata records the executing machine/login; review fresh outputs before public sharing. This publication uses sanitized evidence files and contains no database credentials.
