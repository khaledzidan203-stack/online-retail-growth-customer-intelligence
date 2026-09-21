# SQL portfolio

The SQL Server database is `OnlineRetailAnalytics`. Its layers preserve canonical transaction lineage, apply governed staging types and expose a dimensional analytical model.

## Execution order

Run from the repository root using the [Python orchestration](../src/README.md), or execute the listed SQL scripts in order in an authorized development database. Setup and load scripts can replace existing project data.

| Stage | SQL source | Orchestration |
|---|---|---|
| Database and schemas | [001_create_database.sql](ddl/001_create_database.sql), [002_create_schemas.sql](ddl/002_create_schemas.sql) | load_sql_server.py |
| Canonical raw landing | [010_create_raw_transaction.sql](raw/010_create_raw_transaction.sql) | load_sql_server.py loads the canonical Parquet |
| Typed staging | [020_create_staging_transaction.sql](staging/020_create_staging_transaction.sql) | load_sql_server.py |
| Four dimensions | [030_create_dimensions.sql](analytics/030_create_dimensions.sql) | load_sql_server.py |
| Transaction fact | [040_create_fact_transaction.sql](analytics/040_create_fact_transaction.sql) | load_sql_server.py |
| Foundation reconciliation | [090_validate_checkpoint3.sql](validation/090_validate_checkpoint3.sql) | load_sql_server.py |
| Business views | [100 KPI](analysis/100_kpi_overview.sql), [110 time](analysis/110_time_analysis.sql), [120 product](analysis/120_product_analysis.sql), [130 customer](analysis/130_customer_analysis.sql), [140 country](analysis/140_country_analysis.sql), [150 cancellations](analysis/150_cancellation_analysis.sql) | export_sql_analysis.py |
| Concentration queries | [160_concentration_analysis.sql](analysis/160_concentration_analysis.sql) | Optional read-only queries after view creation |
| Analysis reconciliation | [190_validate_checkpoint4.sql](validation/190_validate_checkpoint4.sql) | export_sql_analysis.py |
| Customer analytics | [250_create_customer_analytics.sql](analytics/250_create_customer_analytics.sql) | publish_customer_analytics.py, after Python RFM/cohort processing |
| Customer reconciliation | [290_validate_checkpoint6a.sql](validation/290_validate_checkpoint6a.sql) | publish_customer_analytics.py |

## Analytical scope

DimDate, DimCustomer, DimProduct and DimCountry support FactTransaction at transaction-line grain. CustomerRFM, CustomerCohort and CustomerRepeatBehavior publish validated customer-level outputs. CohortRetention and CohortRevenue preserve cohort-period grain; Customer360 supports combined customer review.

Sales eligibility, cancellation treatment, anonymous activity and exception classes follow the existing [governance rules](../docs/data_quality/TRANSACTION_CLASSIFICATION.md). SQL provides the reference baseline for [DAX validation](../docs/validation/CHECKPOINT_6B1B_DAX_VALIDATION.md) and [Excel exports](../outputs/management/README.md).

The publication preserves SQL business logic. See the [data model](../docs/data_model.md) and [SQL model documentation](../docs/sql_model.md).
