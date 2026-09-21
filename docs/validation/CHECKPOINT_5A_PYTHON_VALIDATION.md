# Checkpoint 5A Python Validation

## Result

Overall status: PASS

| KPI | Python | SQL baseline | Status |
|---|---:|---:|:---:|
| Sales Revenue | 19,701,685.507 | 19,701,685.507 | PASS |
| Units Sold | 11,221,960 | 11,221,960 | PASS |
| Orders | 39,519 | 39,519 | PASS |
| Sales-known customers | 5,852 | 5,852 | PASS |
| Average Order Value | 498.53704565 | 498.53704564 | PASS |
| Known-customer sales revenue | 17,125,672.047 | 17,125,672.047 | PASS |
| Repeat customers | 4,234 | 4,234 | PASS |
| One-time customers | 1,618 | 1,618 | PASS |
| Cancellation Value | 719,692.94 | 719,692.94 | PASS |
| Cancellation Invoices | 7,406 | 7,406 | PASS |
| Cancellation Value Rate | 3.524213% | 3.524200% | PASS |

Floating-point comparisons use a 0.0001 tolerance for decimal metrics. No mismatch was silently accepted.

## Analytical controls

- SQL Server is the source; the raw Excel workbook was not reread.
- Python did not recreate cleaning or classification rules.
- Distribution analysis operates at order, customer, product, country, cancellation, daily, weekly, and monthly grains.
- No outlier or duplicate row was removed from official metrics.
- Missing Customer IDs were not imputed.
- Operational stock adjustments were not treated as cancellations.
- No RFM, cohort, retention, forecast, or machine-learning model was created.

## Outputs

- checkpoint5a_python_validation.csv
- checkpoint5a_distribution_summary.csv
- checkpoint5a_anomaly_analysis.csv
- checkpoint5a_sensitivity_analysis.csv
- checkpoint5a_forecasting_readiness.json
- checkpoint5a_eda_summary.json
- Eight focused figures under outputs/figures/
