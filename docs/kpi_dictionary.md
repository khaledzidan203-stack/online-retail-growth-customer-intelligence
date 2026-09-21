# KPI dictionary

See [governed KPI definitions](kpis/KPI_DICTIONARY.md) and the [DAX measure dictionary](powerbi/DAX_MEASURE_DICTIONARY.md) for complete formulas, SQL baselines and caveats.

| KPI | Definition |
|---|---|
| Sales Revenue | Sum LineAmount for sales-eligible merchandise. |
| Units Sold | Sum eligible merchandise quantity. |
| Orders | Distinct invoices for eligible sales. |
| Sales Customers | Distinct known customers with eligible sales. |
| Average Order Value | Sales Revenue / Orders. |
| Repeat Customer Rate | Repeat customers / (repeat + one-time sales customers). |
| Cancellation Value | Sum absolute LineAmount for eligible customer cancellations. |
| Cancellation Value Rate | Cancellation Value / (Sales Revenue + Cancellation Value). |
| Anonymous Sales Revenue | Eligible sales with unknown customer ID. |

Duplicate rows remain in official totals. Monetary values are source-currency units. Group counts and rates are not generally additive.
