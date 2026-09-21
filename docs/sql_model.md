# SQL model

## Layers and execution

UCI workbook → Python profiling/canonical cleaning → raw → staging → analytics.

Existing scripts remain in logical order:

1. Database/schemas: sql/ddl/001_create_database.sql and 002_create_schemas.sql.
2. Raw landing: sql/raw/010_create_raw_transaction.sql.
3. Python ingestion and cleaning: src/ingestion/ and src/cleaning/.
4. Staging: sql/staging/020_create_staging_transaction.sql.
5. Dimensions: sql/analytics/030_create_dimensions.sql.
6. Fact: sql/analytics/040_create_fact_transaction.sql.
7. Customer RFM/cohort/repeat: sql/analytics/250_create_customer_analytics.sql and src/ingestion/publish_customer_analytics.py.
8. Reconciliation: sql/validation/090_validate_checkpoint3.sql, 190_validate_checkpoint4.sql and 290_validate_checkpoint6a.sql.

Views under sql/analysis/ define KPI, period, product, customer, country, cancellation and concentration results. Run setup scripts only in a suitably authorized development SQL Server.

## Relationships

Power BI has seven active, single-direction many-to-one relationships: FactTransaction → DimDate, DimCustomer, DimProduct and DimCountry; CustomerRFM, CustomerCohort and CustomerRepeatBehavior → DimCustomer. The customer analytics tables are unique by CustomerKey. CohortRetention and CohortRevenue are disconnected. SQL foreign-key metadata does not encode Power BI filter direction.
