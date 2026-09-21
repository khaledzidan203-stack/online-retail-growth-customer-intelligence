# KPI Dictionary

All official totals preserve exact-duplicate-flagged rows. Monetary units are source-currency values; the dataset does not identify a currency code.

## Merchandise sales KPIs

| KPI | Business definition | Formula | Source and grain | Population / filters | Unit | Limitation |
|---|---|---|---|---|---|---|
| Sales Revenue | Value of approved merchandise sales. | Sum LineAmount | FactTransaction; transaction line | IsSalesEligible = 1 | Source currency | Includes preserved duplicate sensitivity; excludes cancellations and non-merchandise. |
| Units Sold | Merchandise units on approved sales. | Sum Quantity | FactTransaction; transaction line | IsSalesEligible = 1 | Units | Wholesale-scale quantities and extreme orders can strongly affect averages. |
| Orders | Distinct approved merchandise-sale invoices. | Count distinct Invoice | FactTransaction; invoice | IsSalesEligible = 1 | Orders | Invoice is a source identifier, not a generated order key. |
| Known Customers | Customers with at least one customer-eligible sale. | Count distinct CustomerKey | FactTransaction; customer | IsCustomerAnalyticsEligible = 1 | Customers | Differs from the 5,942-customer model population because not every known customer has an eligible sale. |
| Average Order Value | Mean merchandise sales value per eligible order. | Sales Revenue / Orders | KPI overview; order | IsSalesEligible = 1 | Source currency per order | Sensitive to unusually large wholesale orders. |
| Average Units per Order | Mean merchandise units per eligible order. | Units Sold / Orders | KPI overview; order | IsSalesEligible = 1 | Units per order | Sensitive to unusually large quantities. |
| Revenue per Known Customer | Mean eligible sales revenue among customers with eligible sales. | Known-customer Sales Revenue / Sales Known Customers | CustomerPerformance; customer | IsCustomerAnalyticsEligible = 1 | Source currency per customer | Excludes merchandise revenue with missing Customer ID. |
| Orders per Known Customer | Mean distinct eligible orders per sales customer. | Sum customer Orders / Sales Known Customers | CustomerPerformance; customer | IsCustomerAnalyticsEligible = 1 | Orders per customer | Does not measure retention timing. |

## Customer KPIs

| KPI | Business definition | Formula | Source and grain | Population / filters | Unit | Limitation |
|---|---|---|---|---|---|---|
| One-time Customers | Customers with exactly one eligible merchandise order. | Count customers where Orders = 1 | CustomerPerformance; customer | IsCustomerAnalyticsEligible = 1 | Customers | Order history is limited to the dataset period. |
| Repeat Customers | Customers with more than one eligible merchandise order. | Count customers where Orders > 1 | CustomerPerformance; customer | IsCustomerAnalyticsEligible = 1 | Customers | Not an RFM or cohort segment. |
| Repeat Customer Rate | Share of sales customers with more than one eligible order. | Repeat Customers / (One-time + Repeat Customers) | KPI overview; customer | IsCustomerAnalyticsEligible = 1 | Percentage | Excludes missing Customer IDs and customers without an eligible sale. |
| Average Purchase Frequency | Mean eligible order count among sales customers. | Sum customer Orders / Sales Known Customers | CustomerPerformance; customer | IsCustomerAnalyticsEligible = 1 | Orders per customer | Dataset-window measure; not annualized. |
| Average Revenue per Known Customer | Mean eligible revenue among sales customers. | Sum customer Sales Revenue / Sales Known Customers | CustomerPerformance; customer | IsCustomerAnalyticsEligible = 1 | Source currency per customer | Customer totals are lower than total merchandise revenue due to missing IDs. |

## Cancellation KPIs

| KPI | Business definition | Formula | Source and grain | Population / filters | Unit | Limitation |
|---|---|---|---|---|---|---|
| Cancellation Value | Absolute value of approved customer cancellations. | Sum absolute LineAmount | FactTransaction; transaction line | IsCancellationEligible = 1 | Source currency | Does not include operational stock adjustments. |
| Cancellation Units | Absolute quantity on approved customer cancellations. | Sum absolute Quantity | FactTransaction; transaction line | IsCancellationEligible = 1 | Units | Does not imply all cancelled units were physically returned. |
| Cancellation Invoices | Distinct approved cancellation invoices. | Count distinct Invoice | FactTransaction; invoice | IsCancellationEligible = 1 | Invoices | C-prefixed non-merchandise activity is excluded by precedence. |
| Customers with Cancellations | Known customers linked to an approved cancellation. | Count distinct non-null CustomerKey | FactTransaction; customer | IsCancellationEligible = 1 | Customers | Excludes cancellations with missing Customer ID. |
| Cancellation Value Rate | Cancellation value relative to gross sales-plus-cancellation exposure. | Absolute Cancellation Value / (Sales Revenue + Absolute Cancellation Value) | KPI overview or selected time/market grain | Approved sales and cancellation populations | Percentage | This governed denominator is not net revenue and must not be replaced by cancellation value divided by sales revenue. |

## Shared analytical rules

- Product rankings include only DimProduct ItemClass = MERCHANDISE and approved sales/cancellation flags.
- Customer analysis uses only IsCustomerAnalyticsEligible = 1.
- Country cancellation-rate ranking requires at least 100 eligible sales orders.
- Revenue share uses the relevant approved population at the displayed grain.
- Cumulative shares use descending revenue with a deterministic business-key tie-break.
- Operational stock adjustments remain separate from customer cancellations.
