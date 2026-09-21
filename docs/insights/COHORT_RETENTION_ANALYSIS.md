# Cohort and Retention Analysis

## Scope and definitions

Checkpoint 5C uses only SQL transactions where `IsCustomerAnalyticsEligible = 1`: eligible merchandise sales associated with known customers. Anonymous purchases, cancellations, non-merchandise, operational/accounting adjustments, zero-price merchandise, and test records are excluded.

- **CustomerFirstPurchaseDate:** earliest eligible `InvoiceDate` observed for a customer.
- **AcquisitionCohort:** calendar month of the observed first eligible purchase.
- **ActivityMonth:** calendar month containing an eligible customer purchase.
- **CohortIndex:** calendar-month difference between AcquisitionCohort and ActivityMonth; acquisition month is Month 0.
- **ActiveCustomers:** distinct purchasing customers in the cohort-period cell. Multiple purchases in one month count once.
- **RetentionRate:** ActiveCustomers divided by the original CohortSize. This is classic period retention, not survival retention; inactive customers are not carried forward.

The cohort range is 2009-12 through 2011-12 and contains 25 monthly cohorts. All 5,852 customers have exactly one acquisition cohort.

## Observation and censoring policy

The dataset covers 2009-12-01 through 2011-12-09. Observed cohort months with no active customers are represented as zero activity. Future months are not emitted and are not treated as zero.

- The 2009-12 cohort is left-boundary affected. Its 951 customers include customers whose true first purchase may predate the dataset, so it cannot be interpreted as a clean acquisition cohort.
- The 2011-12 cohort and every cohort cell whose ActivityMonth is 2011-12 are partial through December 9.
- Cross-cohort checkpoint metrics exclude cells observed only in partial December 2011.
- Recent cohorts have less lifecycle and repeat-purchase exposure. Lifecycle revenue and observed repeat rates are therefore right-censored.

## Retention results

Weighted retention divides total active customers by total original customers among cohorts eligible for the checkpoint. Median retention gives the median eligible cohort rate without treating unobserved periods as zero.

| Period | Eligible cohorts | Weighted retention | Median cohort retention |
|---|---:|---:|---:|
| Month 1 | 23 | 23.34% | 20.79% |
| Month 2 | 22 | 23.60% | 22.00% |
| Month 3 | 21 | 24.98% | 20.11% |
| Month 6 | 18 | 22.17% | 16.96% |
| Month 12 | 12 | 22.74% | 17.25% |

Period retention does not decay monotonically: different customers may return in later periods after being inactive in an earlier month. Across sufficiently observed cohorts, weighted retention remains broadly in the low-to-mid 20% range, while the median falls below 17.5% at Months 6 and 12. This difference reflects the influence of larger and stronger-retaining cohorts.

## Cohort comparison

For a consistent mature comparison, the 2009-12 boundary cohort is excluded and cohorts must have complete Month 1, Month 3, and Month 6 observations. Using the descriptive mean of these three rates only as a comparison aid:

- 2010-01 is strongest at 26.63%, with Month 1/3/6 retention of 21.47%, 31.52%, and 26.90%.
- 2010-12 is weakest at 7.89%, with Month 1/3/6 retention of 9.21%, 9.21%, and 5.26%.
- 2010-08 has the highest mature Month 3 rate at 32.52%.
- 2010-04 has the highest mature Month 6 rate at 27.55%.
- Recent 2011-09 and 2011-10 cohorts show observed Month 1 rates of 27.13% and 31.67%, but lack complete Month 3/6 follow-up and are not ranked as mature cohorts.

Acquisition cohorts around high-sales periods show different observed retention patterns, but this analysis does not establish that season or sales volume caused those differences.

## Repeat-purchase timing

Of 5,852 customers, 4,234 recorded a second eligible invoice and 1,618 did not during the observation window. The observed repeat-purchase rate is 72.35%.

Among customers with a second purchase, days from first to second eligible purchase are:

| Statistic | Days |
|---|---:|
| Mean | 99.02 |
| P25 | 21 |
| Median | 57 |
| P75 | 133 |
| P90 | 260 |

Of all eligible customers, 22.66% repeated within 30 days, 37.35% within 60 days, 45.90% within 90 days, and 59.89% within 180 days. These are observed-window rates, not fixed behavioral probabilities: customers acquired late in the dataset have less time to repeat.

## Revenue and order lifecycle

Revenue is reported as **Cohort Revenue** and **Revenue per Original Cohort Customer**; it is not labeled revenue retention. All cohort cells reconcile to 17,125,672.047 revenue and 36,597 orders.

The boundary-affected 2009-12 cohort contributes 8,334,307.306, or 48.67% of known-customer revenue. This reflects its large size, long observation window, and likely inclusion of pre-existing customers, so it should not be treated as evidence of superior acquisition quality. Excluding that boundary cohort, 2010-03 and 2010-01 have the largest observed lifecycle revenue at 1,301,009.921 and 1,283,400.042.

The 2010-09 cohort produced 586,430.481 and 2,453.68 revenue per original customer despite relatively low Month 3 and Month 6 retention of 12.97% and 13.81%. This shows that customer retention and revenue contribution can diverge descriptively. Lifecycle revenue comparisons remain exposure-dependent because older cohorts have more observed months.

## Analytical interpretation and limitations

- Most original cohort customers are not active in any given later month, leaving meaningful room to study repeat engagement in future decision work.
- The 57-day median to second purchase suggests repeat behavior often occurs beyond a single 30-day window.
- Period rates fluctuate rather than forming a survival curve; Month 3 exceeding Month 1 does not imply recovered customers remained continuously active.
- No causal claims are made about season, acquisition quality, marketing, or the drivers of retention.
- Monetary results measure revenue rather than profit, margin, or lifetime value.
- Approved duplicate preservation and transaction classification remain unchanged.

## SQL and Power BI preparation

No cohort output has been loaded into SQL. Recommended future analytical grains are:

- `analytics.CustomerCohort`: one row per known customer, using the customer repeat-timing output as the foundation.
- `analytics.CohortRetention`: one row per AcquisitionCohort × CohortIndex, retaining ActivityMonth and partial-observation flags.

