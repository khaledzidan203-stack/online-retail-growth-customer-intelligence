# Governed BI Analytical Layer

## Consumption contract

The `OnlineRetailAnalytics.analytics` schema is the governed consumption layer for future Excel and Power BI work. RFM and cohort results originate from the approved Python outputs and are published by `src/ingestion/publish_customer_analytics.py`; SQL does not independently recalculate the models.

**Power BI must consume these governed tables and views rather than reimplementing RFM scoring, segmentation, acquisition cohorts, or retention logic in DAX.**

## Governed objects

| Object | Grain | Key | Purpose | Relationships and intended BI usage |
|---|---|---|---|---|
| `analytics.FactTransaction` | One governed canonical transaction line | `TransactionLineKey` | Sales, cancellation, product, country, date, lineage, eligibility, and duplicate-sensitive analysis. | Many-to-one relationships to Date, Customer, Product, and Country. Use for transaction and aggregate measures; filter with governed eligibility flags. |
| `analytics.DimDate` | One calendar date | `DateKey`; unique `FullDate` | Shared calendar attributes from 2009-12-01 through 2011-12-09. | One-to-many to FactTransaction. Use for calendar slicing and time intelligence with partial-period caveats. |
| `analytics.DimCustomer` | One known source CustomerID | `CustomerKey`; unique `CustomerID` | Conformed customer identity for all known source customers. | One-to-many to FactTransaction; one-to-one to each published customer table for the 5,852 eligible-sales customers. The additional 90 known IDs are intentionally not forced into customer analytics. |
| `analytics.DimProduct` | One governed normalized StockCode | `ProductKey`; unique `StockCode` | Product identity, representative description, and governed item class. | One-to-many to FactTransaction. Use for product analysis. |
| `analytics.DimCountry` | One governed normalized country | `CountryKey`; unique `Country` | Country identity without invented geographic hierarchy. | One-to-many to FactTransaction. Use for geographic slicing. |
| `analytics.CustomerRFM` | One eligible known customer | `CustomerKey`; unique `CustomerID` | Published RFM reference date, measures, scores, code, segment, purchase span, units, and average order value. | One-to-one foreign key to DimCustomer. Use the stored Segment and scores directly; do not recreate segmentation in DAX. |
| `analytics.CustomerCohort` | One eligible known customer | `CustomerKey`; unique `CustomerID` | Published first observed eligible purchase, acquisition cohort, and left-boundary flag. | One-to-one foreign key to DimCustomer. Use for cohort membership; preserve the 2009-12 boundary warning. |
| `analytics.CustomerRepeatBehavior` | One eligible known customer | `CustomerKey`; unique `CustomerID` | Published first/second purchase dates, repeat flag, and days to second purchase. | One-to-one foreign key to DimCustomer. Null second purchase fields mean no repeat was observed; they are not imputed. |
| `analytics.CohortRetention` | One AcquisitionCohort × CohortIndex | Composite `(AcquisitionCohort, CohortIndex)` | Published cohort size, distinct active customers, period-retention rate, ActivityMonth, and observation flags. | Standalone analytical summary; no artificial customer foreign key. Use for retention matrices and cohort trends. Future unobserved periods are absent. |
| `analytics.CohortRevenue` | One AcquisitionCohort × CohortIndex | Composite `(AcquisitionCohort, CohortIndex)` | Published cohort revenue, orders, per-original-customer measures, and observation flags. | Standalone analytical summary; no artificial customer foreign key. Use for cohort lifecycle value, never under the label “revenue retention.” |

## Customer 360 view

`analytics.vw_Customer360` joins only DimCustomer and the three one-row-per-customer analytical tables. It contains 5,852 rows and preserves one row per eligible known customer. It exposes customer identity, RFM measures and segment, acquisition cohort and boundary flag, and repeat-purchase behavior without joining FactTransaction or multiplying customer rows.

Use the view for customer lists and segment/cohort/repeat cross-analysis. Use the underlying tables when a star-schema relationship is preferable in the semantic model.

## Relationship guidance

- CustomerRFM, CustomerCohort, and CustomerRepeatBehavior enforce foreign keys to DimCustomer and unique CustomerID constraints.
- CohortRetention and CohortRevenue are aggregate fact-like tables sharing the same composite grain. They should not be related to DimCustomer.
- Do not connect customer summary tables directly to FactTransaction on CustomerID in a way that creates many-to-many filtering or measure multiplication. Route customer relationships through DimCustomer.
- No destructive cascades are defined.

## Boundary and population semantics

- Customer analytics contain 5,852 customers with eligible merchandise sales, while DimCustomer contains 5,942 known source IDs.
- `IsLeftBoundaryAffected = 1` identifies the 951 customers first observed in 2009-12; no earlier acquisition date is inferred.
- Cohort cells observed in December 2011 are flagged partial through 2011-12-09.
- Anonymous customers do not appear in any customer analytical table.

## Reproducible publication

1. Run the approved RFM and cohort pipelines to create the governed lightweight outputs.
2. Run `src/ingestion/publish_customer_analytics.py`.
3. The publisher hashes and validates the approved sources, resolves CustomerID to DimCustomer.CustomerKey, creates the analytical SQL objects, replaces their contents transactionally, and runs `sql/validation/290_validate_checkpoint6a.sql`.
4. Review `outputs/checkpoint6a_customer_analytics_sql.json` before downstream consumption.

If the base dimensions are rebuilt, `sql/analytics/030_create_dimensions.sql` clears dependent published tables before replacing DimCustomer. The customer analytics publisher must then be rerun.

