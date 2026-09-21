# SQL Server Analytical Foundation

## Platform and source

- Instance: local default instance khalez_zidan, addressed as localhost.
- Authentication: Windows Authentication.
- Database: OnlineRetailAnalytics.
- Schemas: raw, staging, analytics.
- Governed source: data/interim/canonical_transactions.parquet.

The SQL load does not read or re-clean the Excel workbook. The Python loader transfers the approved canonical columns in batches and performs only the decimal-scale conversion required by the SQL column types.

## Layer design

| Object | Grain | Purpose |
|---|---|---|
| raw.OnlineRetailTransaction | One governed canonical transaction line | Faithful relational landing with source lineage, raw/normalized values, classifications, flags, and duplicate metadata. |
| staging.TransactionCanonical | One governed canonical transaction line | Typed, business-ready canonical projection used to load dimensions and fact. |
| analytics.DimDate | One calendar date | Complete calendar from 2009-12-01 through 2011-12-09. |
| analytics.DimCustomer | One known CustomerID | Known customers only; no RFM or segmentation attributes. |
| analytics.DimProduct | One governed normalized StockCode | Representative description and governed ItemClass. |
| analytics.DimCountry | One governed normalized Country | Country business key only; no invented regions. |
| analytics.FactTransaction | One governed canonical transaction line | Transaction identifiers, measures, classifications, lineage, eligibility flags, and duplicate sensitivity flags. |

## Keys and relationships

- DimDate uses YYYYMMDD DateKey and a unique FullDate.
- DimCustomer, DimProduct, and DimCountry use integer surrogate primary keys with unique business keys.
- FactTransaction uses TransactionLineKey as its primary key, retaining the one-to-one lineage from raw and staging.
- FactTransaction has non-null Date, Product, and Country foreign keys.
- CustomerKey is nullable. Missing source CustomerIDs do not receive a fabricated customer member; IsKnownCustomer distinguishes the 809,561 known-customer rows from the 235,287 unknown-customer rows.
- No foreign key uses a destructive cascade.

## Data types

Invoice, StockCode, and CustomerID are stored as text identifiers. InvoiceDate uses DATETIME2(0), Quantity uses INT, flags use BIT, Price uses DECIMAL(19,8), and LineAmount uses DECIMAL(28,8). Decimal scale conversion removes binary floating-point artifacts while retaining more precision than the governed source values require.

## Product description rule

For each governed StockCode, DimProduct selects the most frequently occurring non-null normalized Description. Ties are resolved deterministically by ascending Description. If a code has no non-null description, RepresentativeDescription remains null.

There are 1,188 StockCodes with multiple normalized descriptions. SQL validation independently recomputes the rule and reports zero representative-description mismatches.

The governed Parquet contains 5,131 distinct normalized StockCodes. This differs from the Checkpoint 1 trim-only count of 5,304 because Checkpoint 2 also uppercases StockCode, collapsing 173 case-only variants. The SQL product dimension follows the governed Parquet and records the earlier baseline comparison as REVIEW.

## Duplicate policy

All exact repeated rows are preserved. IsExactDuplicateAfterFirst remains available as a data-quality sensitivity flag, but official analytical totals use the complete canonical population and do not silently exclude flagged rows.

## Reproducible execution order

1. sql/ddl/001_create_database.sql
2. sql/ddl/002_create_schemas.sql
3. sql/raw/010_create_raw_transaction.sql
4. src/ingestion/load_sql_server.py loads Parquet into raw in batches.
5. sql/staging/020_create_staging_transaction.sql
6. sql/analytics/030_create_dimensions.sql
7. sql/analytics/040_create_fact_transaction.sql
8. sql/validation/090_validate_checkpoint3.sql

The loader uses Windows Authentication and accepts server, driver, Parquet path, output path, and batch-size arguments. It does not change SQL Server configuration or security.
