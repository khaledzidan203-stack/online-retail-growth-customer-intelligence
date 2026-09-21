# Project Index

> Historical implementation index. For the completed ten-page portfolio, use the [current README](../../README.md) and [validation overview](../validation.md). Paths in historical notes refer to the original project root.

## Project Name

Online Retail Growth & Customer Intelligence

## Project Goal

Create a governed analytics solution for sales, customer, product, market, cancellation, and retention decisions using the UCI Online Retail II transactions.

## Current Phase

Power BI Page 02 — Executive Overview

## Completed Work

- Created the checkpoint project structure.
- Relocated the source workbook without changing its bytes and recorded its SHA-256.
- Added a reusable, non-cleaning profiling script.
- Reproduced the cross-sheet overlap and in-memory canonical structural view.
- Wrote machine-readable results and evidence-based discovery documentation.
- Initialized the local Git repository and closed Checkpoint 1 with commit e1dfec7; nothing was pushed.
- Built a lineage-preserving normalized and classified canonical Parquet dataset.
- Added governed item mapping, transaction precedence, analytical flags, duplicate flags, and reconciliation outputs.
- Closed approved Checkpoint 2 with local commit aab96a1; nothing was pushed.
- Created the OnlineRetailAnalytics database with raw, staging, and analytics schemas.
- Loaded the governed Parquet source and built validated Date, Customer, Product, and Country dimensions plus the transaction fact.
- Added reproducible SQL DDL/load/validation scripts and machine-readable SQL reconciliation.
- Closed approved Checkpoint 3 with local commit 55de446; nothing was pushed.
- Added governed reusable SQL views for KPI, time, product, customer, country, and cancellation analysis.
- Added product/customer/country Pareto analysis, like-for-like time comparison, and concise machine-readable exports.
- Added the KPI dictionary, evidence-based SQL analysis baseline, and independent Checkpoint 4 validation.
- Closed approved Checkpoint 4 with local commit fbd8171; nothing was pushed.
- Added reusable SQL-sourced Python validation and EDA modules.
- Added distribution profiling, anomaly investigation, duplicate and missing-customer sensitivity, and time-series readiness assessment.
- Added concise machine-readable outputs and eight focused analytical figures.
- Closed approved Checkpoint 5A with local commit 7cfc4c5; nothing was pushed.
- Added reproducible, SQL-sourced RFM scoring for all 5,852 customer-analytics-eligible customers.
- Added nine exhaustive business segments, customer and segment outputs, reconciliation evidence, and three focused figures.
- Closed approved Checkpoint 5B with local commit 720e7f4; nothing was pushed.
- Added governed monthly acquisition cohorts, classic period retention, lifecycle revenue/orders, and repeat-purchase timing.
- Added censor-aware checkpoint metrics, reusable cohort outputs, four focused figures, and full SQL reconciliation.
- Closed approved Checkpoint 5C with local commit 728fc18; nothing was pushed.
- Published validated RFM, cohort, cohort-revenue, and repeat-purchase outputs into five governed SQL analytical tables.
- Added enforced customer-key relationships, a one-row-per-customer Customer360 view, reproducible publication code, and 35 SQL validation checks.
- Closed approved Checkpoint 6A with local commit ed5a5af; nothing was pushed.
- Inspected the user-created PBIP without modification and documented its TMDL model, report baseline, tables, columns, relationships, Auto Date/Time objects, and semantic-model risks.
- Hardened the PBIP semantic model by removing Auto Date/Time artifacts, governing the sole date dimension, enforcing single-direction relationships, configuring sort behavior, hiding technical columns, and correcting default summarization and neutral formats.
- Added 50 governed explicit DAX measures across core sales, orders, customers, cancellation, time intelligence, RFM, cohort, and data-quality folders without adding calculated columns or tables.
- Reconciled every required measure definition to read-only SQL baselines and confirmed the required values through a read-only runtime DAX query.
- Created the zero-row, relationship-free `_Measures` table and re-homed all 50 explicit measures without changing their DAX expressions or results.
- Created the `INDEX` report Home page with a centered 3 × 3 grid of nine native page-navigation buttons and a basic title/subtitle area.
- Created nine minimal empty destination pages so every INDEX navigation target is valid, without building analytical content.
- Built the authorized `Executive Overview` page with one native Home button, two native slicers, five governed KPI cards, four native analytical charts, and the required partial-period note.
- Preserved the 50-measure, seven-relationship semantic model and explicitly disabled only the unsupported Year/Country slicer interactions with the disconnected RFM segment summary.
- Built the authorized `RFM Segmentation` snapshot page with one Segment slicer, five governed KPI cards, two segment bar charts, one segment-performance table, and one Top 10 customer-value table.
- Refined both RFM tables with native data bars, favorable/neutral/unfavorable arrow rules, readable headers, compact spacing, and suppressed redundant totals.

## Dataset Location

`data/raw/online_retail_II.xlsx` (locally present and Git-ignored)

## Raw Dataset SHA-256

`bcbe73b35f5b7babf197fb0cb983a11f5d9ff929078d4aa53d171b1f2df2e980`

## Expected Raw Counts

- Year 2009-2010: 525,461 rows
- Year 2010-2011: 541,910 rows
- Total: 1,067,371 rows

## Canonical Structural Row Count

1,044,848 rows after excluding Year 2009-2010 records on or after 2010-12-01 and retaining all Year 2010-2011 records. No other rows were removed.

## Important Current Findings

- The excluded cross-sheet overlap is 22,523 exact rows across 1,088 invoices.
- The canonical date range is 2009-12-01 07:45 through 2011-12-09 12:50.
- Raw exact distinct counts are 5,305 StockCodes and 5,698 descriptions.
- Whitespace-trimmed distinct counts are 5,304 StockCodes and 5,655 descriptions.
- Exact duplicates comprise 11,812 extra rows beyond the first occurrence, 22,813 participating rows, and 11,001 duplicate groups.
- The corrected Checkpoint 1 validation passes in full.
- All 1,044,848 canonical rows reconcile across item classes, transaction classes, customer-known status, and duplicate flags.
- Sales eligibility includes 1,015,091 rows and LineAmount 19,701,685.507.
- Cancellation eligibility includes 17,974 rows and absolute LineAmount 719,692.94.
- Duplicate-after-first merchandise sales contribute 57,092.82 of LineAmount and do not change the 39,519 eligible distinct orders.
- No records remain in DQ_REVIEW under the approved precedence.
- SQL raw, staging, and fact tables each reconcile to 1,044,848 rows.
- SQL independently reproduces all approved transaction, monetary, customer, duplicate, and eligible-order baselines.
- DimDate has 739 rows, DimCustomer 5,942, DimCountry 43, and DimProduct 5,131.
- The governed uppercase StockCode count is 5,131 versus the earlier trim-only count of 5,304; 173 case-only variants were collapsed by the approved normalization.
- 1,188 StockCodes have multiple normalized descriptions; the deterministic representative-description rule has zero validation mismatches.
- All Date, Product, and Country relationship breaks, duplicate dimension keys, missing fact rows, and join row multiplication checks equal zero.
- Sales revenue is 19,701,685.507 across 39,519 orders and 11,221,960 units.
- Customer-eligible sales cover 5,852 customers; 72.35% are repeat customers.
- Known-customer revenue is 17,125,672.047; the 2,576,013.46 difference from total sales is attributable to missing Customer IDs.
- Cancellation value is 719,692.94 and the governed cancellation value rate is 3.5242%.
- Product revenue is dispersed, customer revenue is moderately concentrated, and country revenue is highly concentrated in the United Kingdom at 85.56%.
- Python independently reproduces every approved SQL KPI baseline.
- Median order revenue is 301.80 versus mean 498.54; median order units are 149 versus mean 283.96, confirming a strong wholesale tail.
- Anonymous customers contribute 13.08% of merchandise revenue and cannot enter future customer-level analytics.
- The 23843/16446 cancellation contributes 23.41% of cancellation value and 96.75% of December 2011 cancellation value.
- Forecasting readiness is CONDITIONAL because coverage is regular but history is short, boundary periods are partial, and extreme spikes are material.
- The RFM reference date is 2011-12-10, one day after the maximum eligible sales invoice date.
- Champions are 21.55% of known customers and contribute 67.83% of known-customer revenue.
- All 5,852 customers map to exactly one of nine RFM segments; revenue, orders, and units reconcile exactly to governed SQL.
- The cohort range is 2009-12 through 2011-12 across 25 acquisition cohorts; cohort sizes reconcile to all 5,852 known customers.
- Weighted Month 1/3/6/12 retention is 23.34%, 24.98%, 22.17%, and 22.74%, excluding incomplete checkpoint observations.
- The observed repeat-purchase rate is 72.35%; median time to the second eligible purchase is 57 days.
- The 2009-12 cohort is left-boundary affected, and December 2011 is partial through December 9.
- CustomerRFM, CustomerCohort, and CustomerRepeatBehavior each contain 5,852 mapped customers with zero broken or duplicate keys.
- CohortRetention and CohortRevenue each contain 325 observed cohort-period cells; future periods remain absent.
- The Customer360 view preserves exactly 5,852 one-row-per-customer records.
- The PBIP has 10 visible SQL-backed business tables, zero hidden Auto Date/Time tables, seven active M:1 single-direction relationships, zero measures, one page, and zero visuals.
- The model has zero bidirectional and zero many-to-many relationships; customer analytical sources remain unique by CustomerKey in governed SQL while using M:1 semantic relationships for safe single-direction filtering.
- CohortRetention and CohortRevenue are disconnected at their governed AcquisitionCohort × CohortIndex grain.
- DimDate is the sole date table; FullDate is its key date column, MonthName sorts by MonthNumber, and DayName sorts by DayOfWeekNumber.
- The governed measure layer contains 50 explicit measures in eight logical display folders; required SQL baselines reconcile at definition level.
- Runtime DAX validation passes for all required baselines; no validation page or visual was introduced.
- `_Measures` owns all 50 explicit measures, contains only one hidden placeholder column, and has zero relationships.
- The report contains 10 pages: `INDEX`, the built `Executive Overview`, and eight intentionally empty analytical destinations.
- `INDEX` contains nine native navigation buttons and two textboxes; there are no analytical visuals, slicers, broken bindings, navigation errors, or off-canvas visuals.
- `Executive Overview` contains 14 visuals: one title, one native Home button, two slicers, five KPI cards, four analytical charts, and one boundary-period note.
- Both Top 5 charts use native visual Top N filters and descending Sales Revenue sorting; the monthly trend uses ascending YearMonth sorting.
- Executive Overview has zero invalid JSON files, broken bindings, navigation errors, or off-canvas visuals, and all 38 schema-bearing report files pass the official PBIR JSON schemas.

## Important Files

- `src/ingestion/profile_raw_dataset.py`
- `src/cleaning/build_canonical_transactions.py`
- `src/ingestion/load_sql_server.py`
- `config/item_classification.json`
- `outputs/discovery_baseline.json`
- `outputs/checkpoint2_reconciliation.json`
- `outputs/checkpoint3_sql_reconciliation.json`
- `docs/discovery/RAW_DATA_MANIFEST.md`
- `docs/discovery/DATA_DISCOVERY.md`
- `docs/discovery/DATA_DICTIONARY.md`
- `docs/data_quality/DQ_BASELINE.md`
- `docs/data_quality/TRANSACTION_CLASSIFICATION.md`
- `docs/validation/CHECKPOINT_2_RECONCILIATION.md`
- `docs/architecture/SQL_STAR_SCHEMA.md`
- `docs/validation/CHECKPOINT_3_SQL_RECONCILIATION.md`
- `sql/ddl/001_create_database.sql`
- `sql/ddl/002_create_schemas.sql`
- `sql/raw/010_create_raw_transaction.sql`
- `sql/staging/020_create_staging_transaction.sql`
- `sql/analytics/030_create_dimensions.sql`
- `sql/analytics/040_create_fact_transaction.sql`
- `sql/validation/090_validate_checkpoint3.sql`
- `sql/analysis/100_kpi_overview.sql` through `160_concentration_analysis.sql`
- `sql/validation/190_validate_checkpoint4.sql`
- `src/analytics/export_sql_analysis.py`
- `outputs/checkpoint4_sql_analysis.json`
- `docs/kpis/KPI_DICTIONARY.md`
- `docs/insights/SQL_BUSINESS_ANALYSIS_BASELINE.md`
- `docs/validation/CHECKPOINT_4_SQL_ANALYSIS_VALIDATION.md`
- `src/analytics/validation.py`
- `src/analytics/eda.py`
- `outputs/checkpoint5a_eda_summary.json`
- `outputs/checkpoint5a_distribution_summary.csv`
- `outputs/checkpoint5a_sensitivity_analysis.csv`
- `outputs/checkpoint5a_forecasting_readiness.json`
- `docs/insights/PYTHON_EDA_BASELINE.md`
- `docs/validation/CHECKPOINT_5A_PYTHON_VALIDATION.md`
- `src/analytics/rfm.py`
- `outputs/rfm_customer_segments.csv`
- `outputs/rfm_segment_summary.csv`
- `outputs/rfm_score_boundaries.json`
- `docs/insights/RFM_CUSTOMER_SEGMENTATION.md`
- `docs/validation/CHECKPOINT_5B_RFM_VALIDATION.md`
- `src/analytics/cohort.py`
- `outputs/cohort_customer_retention.csv`
- `outputs/cohort_revenue.csv`
- `outputs/customer_repeat_timing.csv`
- `outputs/cohort_summary.csv`
- `docs/insights/COHORT_RETENTION_ANALYSIS.md`
- `docs/validation/CHECKPOINT_5C_COHORT_VALIDATION.md`
- `src/ingestion/publish_customer_analytics.py`
- `sql/analytics/250_create_customer_analytics.sql`
- `sql/validation/290_validate_checkpoint6a.sql`
- `outputs/checkpoint6a_customer_analytics_sql.json`
- `docs/architecture/BI_ANALYTICAL_LAYER.md`
- `docs/validation/CHECKPOINT_6A_CUSTOMER_ANALYTICS_SQL.md`
- `docs/powerbi/POWER_BI_BASELINE.md`
- `docs/validation/CHECKPOINT_6B0_POWER_BI_BASELINE.md`
- `docs/powerbi/POWER_BI_SEMANTIC_MODEL.md`
- `docs/validation/CHECKPOINT_6B1A_SEMANTIC_MODEL.md`
- `docs/powerbi/DAX_MEASURE_DICTIONARY.md`
- `docs/validation/CHECKPOINT_6B1B_DAX_VALIDATION.md`
- `docs/powerbi/REPORT_PAGE_INDEX.md`
- `docs/powerbi/PAGE_EXECUTIVE_OVERVIEW.md`

## Known Risks

- Source text contains whitespace variants that affect distinct counts.
- Exact duplicates remain present by approved policy and must be treated as a documented sensitivity in downstream analysis.
- PADS and DCG* remain merchandise by instruction and may need later evidence-based review.
- Negative quantities include both customer cancellations and operational/accounting activity.
- Missing customer and description values constrain customer/product analysis.
- Special StockCodes do not all represent merchandise.
- Calendar 2009 and 2011 are partial and cannot be compared naively with full 2010.
- A single large StockCode 23843 sale/cancellation materially affects cancellation concentration and December 2011 rates.
- Customer analytics necessarily exclude 13.08% of merchandise revenue associated with anonymous sales.
- Means are materially influenced by wholesale/high-value tails and require median and percentile context.
- Acquisition and repeat measures are right-censored; the first and final cohorts also have explicit observation-boundary limitations.
- The `_Measures` placeholder is a technical structural requirement and must remain hidden and data-free.
- All nine analytical destination pages are now individually built; see the page inventory and page-level validation documentation under `docs/powerbi/`.
- Hidden Power BI fields are usability controls, not security controls, and remain accessible to authored DAX.
- Year comparisons require comparable covered periods because 2009 contains only December and 2011 ends on December 9.

## Open Decisions

- Decide whether any merchandise-default special codes require further governed mapping.
- Decide how the governed uppercase StockCode distinction should be communicated in downstream semantic models.
- Decide whether future refreshes should preserve the current RFM rules as a versioned baseline or recalibrate them to each observation window.
- Define how sensitivity findings will be disclosed without replacing official preserved-row KPIs.
- Review the aligned governed measure layer before authorizing report construction.
- Each analytical report page has its own scope and validation documentation; all pages use the native INDEX navigation standard.

## Final Portfolio Status

- Final report QA: 10 pages, 136 visuals, 50 measures, 7 relationships, 15 TMDL files; structural and semantic QA pass.
- Management workbooks reconcile to SQL. See `docs/validation.md` and `outputs/management/management_export_validation.json`.
- Portfolio packaging is prepared. Public GitHub publication is pending account authentication and resolution of personal email addresses in existing commit history.
