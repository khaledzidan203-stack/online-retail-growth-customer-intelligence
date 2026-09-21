# Changelog

## Portfolio publication

- Published the completed analytical project with a recruiter-first README, architecture and data-model diagrams, source guides and reproducible run steps.
- Included all ten real Power BI screenshots and both validated management workbooks.
- Preserved SQL, Python, PBIP, PBIR, TMDL, DAX and Excel analytical values; used an isolated sanitized initial commit with a GitHub noreply identity.
- Consolidated planning/audit documents under docs/project/ in the publication copy. Earlier entries below retain historical checkpoint status.

## Unreleased

- Implemented Market Analysis with five KPIs, overall/non-UK revenue rankings, cancellation-value ranking and market economics table; no model or other-page changes.
- Added Market Analysis documentation; structural checks pass, with exact PBIR 2.12 schema validation blocked by unavailable public schema and Desktop review pending.

- Refined the two RFM tables with native PBIR data bars and arrow-based conditional formatting while keeping numeric values visible.
- Applied reversed favorable logic to Recency, normal favorable logic to Frequency and Monetary, compact table spacing, percentage headers, and no redundant totals.
- Built the `RFM Segmentation` snapshot page at the governed 2011-12-10 reference date using existing CustomerRFM fields and governed measures only.
- Added one Segment slicer, five responsive KPI cards, two segment bar charts, the RFM Segment Performance table, and the Top Customers by RFM Value table without model changes.
- Intentionally omitted Year and Country slicers because RFM is a current snapshot rather than a dynamically re-segmented history.
- Built the `Executive Overview` report page with one native Home button, two native slicers, five governed KPI cards, four native analytical charts, and the required partial-period note.
- Added ascending YearMonth sorting, descending segment/revenue sorting, native Top 5 filters for markets and products, and governed tooltip fields without changing DAX or the semantic model.
- Explicitly disabled Year and Country slicer interactions with the disconnected CustomerRFM segment visual while preserving valid slicer filtering for fact-based visuals.
- Validated all 38 schema-bearing PBIR report files with zero schema errors, broken bindings, navigation errors, or off-canvas visuals; measures remain 50 and relationships remain seven.
- Added the `INDEX` Home page with a basic title/subtitle and nine native page-navigation buttons in a balanced 3 × 3 grid.
- Added nine empty destination pages solely to provide valid navigation targets; no analytical visual, KPI card, chart, or slicer was created.
- Documented the future analytical-page Home-button standard and validated PBIR schemas, navigation targets, bindings, and canvas bounds.
- Added the zero-row, relationship-free `_Measures` table and moved all 50 explicit measures into it with zero DAX-expression changes.
- Preserved all eight logical display folders, aligning the utility folder name to `08 Data Quality & Utility`.
- Re-ran the required measures through the active Power BI Analysis Services model; every SQL ↔ DAX baseline passed after re-homing.
- Added 50 governed explicit DAX measures in eight display folders for sales, orders, customers, cancellation, time intelligence, RFM, cohort, and data-quality analysis.
- Reused the published repeat, RFM, and cohort logic without calculated tables, calculated columns, artificial relationships, or report changes.
- Reconciled required measure definitions to read-only SQL baselines and confirmed them through read-only runtime DAX execution.
- Added the governed DAX measure dictionary and Checkpoint 6B-1B validation evidence; 6B-1B remains uncommitted pending review.
- Hardened the PBIP semantic model to 10 business tables and seven active M:1 single-direction relationships with zero bidirectional or many-to-many paths.
- Disabled Auto Date/Time, removed nine generated date objects and their relationships/variations, and established DimDate/FullDate as the sole governed date strategy.
- Added governed month/day sorting, technical-column hiding, safe default summarization, and neutral display formats without adding measures or changing the report.
- Added the Checkpoint 6B-1A semantic-model specification and validation evidence; 6B-1A remains uncommitted pending review.
- Documented the user-created PBIP baseline without modifying it: 10 visible business tables, 9 hidden auto-date tables, 15 relationships, zero measures, one page, and zero visuals.
- Recorded bidirectional customer-filter, Auto Date/Time, default-aggregation, date-model, and column-hygiene review items for the next semantic-model checkpoint.
- Published approved RFM, cohort, cohort-revenue, and repeat-purchase outputs into governed SQL analytical tables without model recalculation.
- Added customer-key constraints, a one-row-per-customer Customer360 view, source-hash reconciliation, and 35 SQL validation checks.
- Added governed acquisition cohorts, classic monthly period retention, cohort revenue/orders, and repeat-purchase timing.
- Added censor-aware retention summaries, four focused cohort figures, reusable outputs, and complete population/revenue/order validation.
- Added SQL-sourced RFM scoring with tied quantile handling and a reproducible 2011-12-10 reference date.
- Added nine exhaustive customer segments, reconciled customer/segment outputs, three focused figures, and an evidence-based action framework.
- Added SQL-sourced Python KPI validation, distribution EDA, anomaly investigation, and sensitivity analysis.
- Added time-series readiness evidence and eight focused Python figures without creating a forecast.
- Documented anonymous-customer limits and the 23843/16446 cancellation influence.
- Added governed SQL KPI, time, product, customer, country, cancellation, and concentration analyses.
- Added concise Checkpoint 4 exports, KPI definitions, descriptive findings, and population validation.
- Added the OnlineRetailAnalytics SQL Server database foundation with raw, staging, and analytics schemas.
- Added reproducible batched Parquet loading, star-schema DDL, and independent SQL reconciliation.
- Documented the governed 5,131-product result, representative-description rule, and SQL relationship validation.
- Added the governed canonical transaction pipeline and local Parquet output.
- Added reusable item mapping, transaction precedence, analytical flags, and duplicate-impact reconciliation.
- Added Checkpoint 2 machine-readable summaries and documentation.
- Added the Checkpoint 1 project scaffold.
- Protected and fingerprinted the raw workbook.
- Added reproducible baseline profiling and discovery documentation.
- Corrected the baseline to distinguish raw and trimmed distinct counts and to use the independently verified duplicate metrics.

- Corrected Customer Intelligence value/frequency and Top Customers visuals to use the governed fact/dimension model with Year/Country responsiveness.
