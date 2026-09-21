# DAX Measure Dictionary

## Governance

This dictionary defines the governed Checkpoint 6B-1B measure layer and its Checkpoint 6B-1C ownership alignment. All 50 explicit measures are owned by the dedicated `_Measures` table. The table contains zero rows, has no relationships, and has one hidden `Placeholder` text column supplied by a minimal M partition solely to keep the table structurally valid. The "Source table" field below identifies each measure's data dependency, not its owning table.

Revenue formats are neutral because the source currency is not formally governed. Measures preserve existing report filters while intersecting them with the approved eligibility flags. RFM and cohort assignments are consumed from governed SQL tables and are not recalculated in DAX.

## 01 Core Sales

| Measure | Business definition | DAX | Source table | Population | Format | SQL baseline |
|---|---|---|---|---|---|---:|
| Sales Revenue | Approved merchandise sales value. | `CALCULATE(SUM(FactTransaction[LineAmount]), KEEPFILTERS(FactTransaction[IsSalesEligible] = TRUE()))` | FactTransaction | Sales eligible | `#,##0.00` | 19,701,685.507 |
| Average Order Value | Sales revenue per eligible order. | `DIVIDE([Sales Revenue], [Orders])` | FactTransaction | Sales eligible | `#,##0.00` | 498.5370 |

## 02 Orders & Units

| Measure | Business definition | DAX | Source table | Population | Format | SQL baseline |
|---|---|---|---|---|---|---:|
| Units Sold | Units on approved merchandise sales. | `CALCULATE(SUM(FactTransaction[Quantity]), KEEPFILTERS(FactTransaction[IsSalesEligible] = TRUE()))` | FactTransaction | Sales eligible | `#,##0` | 11,221,960 |
| Orders | Distinct approved merchandise-sale invoices. | `CALCULATE(DISTINCTCOUNT(FactTransaction[Invoice]), KEEPFILTERS(FactTransaction[IsSalesEligible] = TRUE()))` | FactTransaction | Sales eligible | `#,##0` | 39,519 |
| Average Units per Order | Eligible units per eligible order. | `DIVIDE([Units Sold], [Orders])` | FactTransaction | Sales eligible | `#,##0.00` | 283.9637 |

## 03 Customers

| Measure | Business definition | DAX | Source table | Population | Format | SQL baseline |
|---|---|---|---|---|---|---:|
| Sales Customers | Distinct customers with an eligible customer-analytics sale. | `CALCULATE(DISTINCTCOUNT(FactTransaction[CustomerKey]), KEEPFILTERS(FactTransaction[IsCustomerAnalyticsEligible] = TRUE()))` | FactTransaction | Customer-analytics eligible | `#,##0` | 5,852 |
| Known Customer Revenue | Sales revenue attributable to the customer-analytics population. | `CALCULATE(SUM(FactTransaction[LineAmount]), KEEPFILTERS(FactTransaction[IsCustomerAnalyticsEligible] = TRUE()))` | FactTransaction | Customer-analytics eligible | `#,##0.00` | 17,125,672.047 |
| Revenue per Known Customer | Known-customer revenue per sales customer. | `DIVIDE([Known Customer Revenue], [Sales Customers])` | FactTransaction | Customer-analytics eligible | `#,##0.00` | 2,926.4648 |
| Orders per Known Customer | Distinct eligible customer orders per sales customer. | `DIVIDE(CALCULATE(DISTINCTCOUNT(FactTransaction[Invoice]), KEEPFILTERS(FactTransaction[IsCustomerAnalyticsEligible] = TRUE())), [Sales Customers])` | FactTransaction | Customer-analytics eligible | `#,##0.00` | 6.2538 |
| Repeat Customers | Customers whose governed repeat record has a repeat purchase. | `CALCULATE(COUNTROWS(CustomerRepeatBehavior), KEEPFILTERS(CustomerRepeatBehavior[HasRepeatPurchase] = TRUE()))` | CustomerRepeatBehavior | Published repeat population | `#,##0` | 4,234 |
| One-Time Customers | Customers whose governed repeat record has no repeat purchase. | `CALCULATE(COUNTROWS(CustomerRepeatBehavior), KEEPFILTERS(CustomerRepeatBehavior[HasRepeatPurchase] = FALSE()))` | CustomerRepeatBehavior | Published repeat population | `#,##0` | 1,618 |
| Repeat Customer Rate | Repeat customers divided by repeat plus one-time customers. | `DIVIDE([Repeat Customers], [Repeat Customers] + [One-Time Customers])` | CustomerRepeatBehavior | Published repeat population | `0.00%` | 72.3513% |

## 04 Cancellation

| Measure | Business definition | DAX | Source table | Population | Format | SQL baseline |
|---|---|---|---|---|---|---:|
| Cancellation Value | Absolute line value of approved customer cancellations. | `CALCULATE(SUMX(FactTransaction, ABS(FactTransaction[LineAmount])), KEEPFILTERS(FactTransaction[IsCancellationEligible] = TRUE()))` | FactTransaction | Cancellation eligible | `#,##0.00` | 719,692.940 |
| Cancellation Units | Absolute quantity on approved customer cancellations. | `CALCULATE(SUMX(FactTransaction, ABS(FactTransaction[Quantity])), KEEPFILTERS(FactTransaction[IsCancellationEligible] = TRUE()))` | FactTransaction | Cancellation eligible | `#,##0` | 469,882 |
| Cancellation Invoices | Distinct approved cancellation invoices. | `CALCULATE(DISTINCTCOUNT(FactTransaction[Invoice]), KEEPFILTERS(FactTransaction[IsCancellationEligible] = TRUE()))` | FactTransaction | Cancellation eligible | `#,##0` | 7,406 |
| Customers with Cancellations | Distinct known customers on approved cancellations. | `CALCULATE(DISTINCTCOUNT(FactTransaction[CustomerKey]), KEEPFILTERS(FactTransaction[IsCancellationEligible] = TRUE()), KEEPFILTERS(FactTransaction[IsKnownCustomer] = TRUE()))` | FactTransaction | Cancellation eligible and known customer | `#,##0` | 2,445 |
| Cancellation Value Rate | Cancellation value divided by sales plus cancellation value. | `DIVIDE([Cancellation Value], [Sales Revenue] + [Cancellation Value])` | FactTransaction | Approved sales and cancellation populations | `0.0000%` | 3.524213% |

## 05 Time Intelligence

| Measure | Business definition | DAX | Source table | Population | Format | SQL baseline |
|---|---|---|---|---|---|---|
| Sales Revenue PY | Sales revenue shifted one year through DimDate. | `CALCULATE([Sales Revenue], DATEADD(DimDate[FullDate], -1, YEAR))` | DimDate / FactTransaction | Sales eligible | `#,##0.00` | Contextual |
| Sales Revenue YoY | Current sales revenue less prior-year sales revenue. | `[Sales Revenue] - [Sales Revenue PY]` | DimDate / FactTransaction | Sales eligible | `#,##0.00` | Contextual |
| Sales Revenue YoY % | Revenue YoY change divided by prior-year revenue. | `DIVIDE([Sales Revenue YoY], [Sales Revenue PY])` | DimDate / FactTransaction | Sales eligible | `0.00%` | Contextual |
| Orders PY | Eligible orders shifted one year through DimDate. | `CALCULATE([Orders], DATEADD(DimDate[FullDate], -1, YEAR))` | DimDate / FactTransaction | Sales eligible | `#,##0` | Contextual |
| Orders YoY % | Eligible-order change divided by prior-year orders. | `DIVIDE([Orders] - [Orders PY], [Orders PY])` | DimDate / FactTransaction | Sales eligible | `0.00%` | Contextual |
| Units Sold PY | Eligible units shifted one year through DimDate. | `CALCULATE([Units Sold], DATEADD(DimDate[FullDate], -1, YEAR))` | DimDate / FactTransaction | Sales eligible | `#,##0` | Contextual |
| Units Sold YoY % | Eligible-unit change divided by prior-year units. | `DIVIDE([Units Sold] - [Units Sold PY], [Units Sold PY])` | DimDate / FactTransaction | Sales eligible | `0.00%` | Contextual |
| Sales Revenue YTD | Eligible sales revenue from year start through current date context. | `TOTALYTD([Sales Revenue], DimDate[FullDate])` | DimDate / FactTransaction | Sales eligible | `#,##0.00` | Contextual |
| Sales Revenue MTD | Eligible sales revenue from month start through current date context. | `TOTALMTD([Sales Revenue], DimDate[FullDate])` | DimDate / FactTransaction | Sales eligible | `#,##0.00` | Contextual |

The dataset begins in December 2009 and ends on 2011-12-09. Time-intelligence measures are mathematically valid, but comparisons require equivalent covered periods.

## 06 RFM

| Measure | Business definition | DAX | Source table | Population | Format | SQL baseline |
|---|---|---|---|---|---|---:|
| RFM Customers | Total governed RFM population, retaining non-segment filters. | `CALCULATE(COUNTROWS(CustomerRFM), REMOVEFILTERS(CustomerRFM[Segment]))` | CustomerRFM | Published RFM population | `#,##0` | 5,852 |
| RFM Revenue | Total governed RFM monetary value, retaining non-segment filters. | `CALCULATE(SUM(CustomerRFM[Monetary]), REMOVEFILTERS(CustomerRFM[Segment]))` | CustomerRFM | Published RFM population | `#,##0.00` | 17,125,672.047 |
| Segment Customers | Governed RFM customers in current segment context. | `COUNTROWS(CustomerRFM)` | CustomerRFM | Current segment context | `#,##0` | Contextual |
| Segment Revenue | Governed RFM monetary value in current segment context. | `SUM(CustomerRFM[Monetary])` | CustomerRFM | Current segment context | `#,##0.00` | Contextual |
| Segment Customer Share | Segment customers divided by RFM customers across segments. | `DIVIDE([Segment Customers], [RFM Customers])` | CustomerRFM | Current segment / RFM population | `0.00%` | Contextual |
| Segment Revenue Share | Segment revenue divided by RFM revenue across segments. | `DIVIDE([Segment Revenue], [RFM Revenue])` | CustomerRFM | Current segment / RFM population | `0.00%` | Contextual |
| Average RFM Recency | Mean published recency in current context. | `AVERAGE(CustomerRFM[Recency])` | CustomerRFM | Published RFM population | `#,##0.00` | Contextual |
| Average RFM Frequency | Mean published frequency in current context. | `AVERAGE(CustomerRFM[Frequency])` | CustomerRFM | Published RFM population | `#,##0.00` | Contextual |
| Average RFM Monetary | Mean published monetary value in current context. | `AVERAGE(CustomerRFM[Monetary])` | CustomerRFM | Published RFM population | `#,##0.00` | Contextual |

## 07 Cohort & Retention

| Measure | Business definition | DAX | Source table | Population | Format | SQL baseline |
|---|---|---|---|---|---|---|
| Cohort Size | Sum of one cohort-size value per visible acquisition cohort. | `SUMX(VALUES(CohortRetention[AcquisitionCohort]), CALCULATE(MAX(CohortRetention[CohortSize])))` | CohortRetention | Visible cohort cells | `#,##0` | Contextual |
| Active Cohort Customers | Sum of active customers across visible cohort-period cells. | `SUM(CohortRetention[ActiveCustomers])` | CohortRetention | Visible cohort cells | `#,##0` | Contextual |
| Retention Rate | Weighted retention across visible cells; sums active customers and cell cohort sizes, never stored rates. | `DIVIDE(SUM(CohortRetention[ActiveCustomers]), SUM(CohortRetention[CohortSize]))` | CohortRetention | Visible cohort cells | `0.00%` | Contextual |
| Cohort Revenue | Revenue across visible cohort-revenue cells. | `SUM(CohortRevenue[Revenue])` | CohortRevenue | Visible cohort-revenue cells | `#,##0.00` | Contextual |
| Revenue per Original Cohort Customer | Visible cohort revenue divided by one size per visible acquisition cohort. | `DIVIDE([Cohort Revenue], SUMX(VALUES(CohortRevenue[AcquisitionCohort]), CALCULATE(MAX(CohortRevenue[CohortSize]))))` | CohortRevenue | Visible cohort-revenue cells | `#,##0.00` | Contextual |
| Cohort Orders | Orders across visible cohort-revenue cells. | `SUM(CohortRevenue[Orders])` | CohortRevenue | Visible cohort-revenue cells | `#,##0` | Contextual |
| Orders per Original Cohort Customer | Visible cohort orders divided by one size per visible acquisition cohort. | `DIVIDE([Cohort Orders], SUMX(VALUES(CohortRevenue[AcquisitionCohort]), CALCULATE(MAX(CohortRevenue[CohortSize]))))` | CohortRevenue | Visible cohort-revenue cells | `#,##0.00` | Contextual |

`CohortRetention` and `CohortRevenue` remain disconnected. Each measure operates only within its own summary-table context; no artificial relationship or DAX cohort reassignment is introduced.

## 08 Data Quality & Utility

| Measure | Business definition | DAX | Source table | Population | Format | SQL baseline |
|---|---|---|---|---|---|---:|
| Canonical Transaction Rows | Canonical fact row count. | `COUNTROWS(FactTransaction)` | FactTransaction | All canonical rows | `#,##0` | 1,044,848 |
| Sales Eligible Rows | Count of approved sales rows. | `CALCULATE(COUNTROWS(FactTransaction), KEEPFILTERS(FactTransaction[IsSalesEligible] = TRUE()))` | FactTransaction | Sales eligible | `#,##0` | 1,015,091 |
| Anonymous Sales Revenue | Approved sales revenue without a known customer. | `CALCULATE(SUM(FactTransaction[LineAmount]), KEEPFILTERS(FactTransaction[IsSalesEligible] = TRUE()), KEEPFILTERS(FactTransaction[IsKnownCustomer] = FALSE()))` | FactTransaction | Sales eligible and unknown customer | `#,##0.00` | 2,576,013.460 |
| Anonymous Sales Revenue % | Anonymous sales revenue divided by sales revenue. | `DIVIDE([Anonymous Sales Revenue], [Sales Revenue])` | FactTransaction | Sales eligible | `0.00%` | 13.0751% |
| Duplicate Flagged Revenue | Sales revenue on exact-duplicate rows after the retained first occurrence. | `CALCULATE(SUM(FactTransaction[LineAmount]), KEEPFILTERS(FactTransaction[IsSalesEligible] = TRUE()), KEEPFILTERS(FactTransaction[IsExactDuplicateAfterFirst] = TRUE()))` | FactTransaction | Sales eligible duplicate-after-first rows | `#,##0.00` | 57,092.820 |
| Duplicate Revenue Impact % | Duplicate flagged revenue divided by sales revenue. | `DIVIDE([Duplicate Flagged Revenue], [Sales Revenue])` | FactTransaction | Sales eligible | `0.00%` | 0.2898% |
| Operational Adjustment Rows | Rows classified as operational stock adjustments. | `CALCULATE(COUNTROWS(FactTransaction), KEEPFILTERS(FactTransaction[TransactionClass] = "OPERATIONAL_STOCK_ADJUSTMENT"))` | FactTransaction | Operational adjustment class | `#,##0` | 3,392 |
| DQ Review Rows | Rows classified for data-quality review, returning zero for an empty population. | `COALESCE(CALCULATE(COUNTROWS(FactTransaction), KEEPFILTERS(FactTransaction[TransactionClass] = "DQ_REVIEW")), 0)` | FactTransaction | DQ review class | `#,##0` | 0 |
