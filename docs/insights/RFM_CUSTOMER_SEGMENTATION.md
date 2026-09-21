# RFM Customer Segmentation

## Scope and population

Checkpoint 5B segments the 5,852 known customers represented by `IsCustomerAnalyticsEligible = 1`. This governed population contains merchandise sales with valid customer identifiers and excludes anonymous sales, cancellations, operational stock movements, non-merchandise, zero-price merchandise, accounting adjustments, and test records.

The output grain is one row per known customer. It is suitable for a future `analytics.CustomerRFM` table, but this checkpoint does not load the output into SQL.

## Reference date and measures

The reproducible reference date is **2011-12-10**, one calendar day after the maximum eligible sales invoice timestamp.

- Recency: calendar days from the reference date to the customer's latest eligible purchase date.
- Frequency: distinct eligible sales invoices.
- Monetary: sum of eligible merchandise-sales `LineAmount`.
- Supporting fields: first and last purchase timestamps, units purchased, active lifespan in calendar days, and average order value.

## Scoring method and observed boundaries

Scores use the observed 20th, 40th, 60th, and 80th percentiles. Duplicate cutpoints are collapsed, and a value equal to a cutpoint remains in the lower value band. This keeps identical raw values together and permits unequal band sizes rather than silently forcing bins. Recency is reverse-scored; Frequency and Monetary are scored in ascending value order.

| Score | Recency days | Frequency orders | Monetary |
|---:|---:|---:|---:|
| 1 | 410–739 | 1 | 2.95–286.60 |
| 2 | 188–409 | 2 | 287.05–605.90 |
| 3 | 60–187 | 3–4 | 606.02–1,212.84 |
| 4 | 22–59 | 5–8 | 1,213.05–2,889.28 |
| 5 | 1–20 | 9–373 | 2,900.58–580,987.04 |

## Exhaustive segment rules

Rules are evaluated in the listed order and are mutually exclusive.

1. Champions: R >= 4, F >= 4, and M >= 4.
2. Loyal Customers: remaining customers with R >= 3 and F >= 4.
3. Potential Loyalists: remaining customers with R >= 4 and F in 2–3.
4. New Customers: remaining customers with R = 5 and F = 1.
5. Promising: remaining customers with R = 4 and F = 1, or R = 3, F in 2–3, and M >= 3.
6. Need Attention: remaining customers with R = 3.
7. At Risk: remaining customers with R <= 2 and F >= 3.
8. Hibernating: remaining customers with R = 2 and F <= 2.
9. Lost: all remaining customers, which resolve to R = 1 and F <= 2.

`RFM_Total` is retained only as a diagnostic and does not determine the segment.

## Segment behavior and contribution

| Segment | Customers | Customer share | Revenue | Revenue share | Avg recency | Avg orders | Avg revenue/customer |
|---|---:|---:|---:|---:|---:|---:|---:|
| Champions | 1,261 | 21.55% | 11,616,420.67 | 67.83% | 20.0 | 17.28 | 9,212.07 |
| Loyal Customers | 594 | 10.15% | 1,719,846.32 | 10.04% | 86.0 | 8.28 | 2,895.36 |
| Potential Loyalists | 716 | 12.24% | 878,554.67 | 5.13% | 25.9 | 2.88 | 1,227.03 |
| New Customers | 78 | 1.33% | 26,369.28 | 0.15% | 12.0 | 1.00 | 338.07 |
| Promising | 455 | 7.78% | 493,527.15 | 2.88% | 84.5 | 2.32 | 1,084.68 |
| Need Attention | 409 | 6.99% | 165,370.77 | 0.97% | 109.6 | 1.66 | 404.33 |
| At Risk | 709 | 12.12% | 1,531,082.34 | 8.94% | 360.0 | 5.49 | 2,159.50 |
| Hibernating | 681 | 11.64% | 299,939.45 | 1.75% | 315.9 | 1.38 | 440.44 |
| Lost | 949 | 16.22% | 394,561.39 | 2.30% | 553.5 | 1.25 | 415.77 |

Champions are 21.55% of customers but contribute 67.83% of known-customer revenue and 59.53% of known-customer orders. Champions plus Loyal Customers represent 31.70% of customers and 77.87% of revenue. At Risk customers retain materially greater historical frequency and value than Hibernating or Lost customers, making the label behaviorally distinct rather than merely old.

The nine segments behave logically: Champions are recent, frequent, and high-value; New Customers are recent single-order customers; and Hibernating/Lost customers are progressively less recent with low engagement. Promising customers have higher average value than Potential Loyalists despite being less recent on average; this follows the explicit monetary-qualified R=3 branch and is an intended prioritization signal, not a contradiction.

## Analytical action framework

| Segment | Descriptive action |
|---|---|
| Champions | Retain, recognize, and test early access or premium service. |
| Loyal Customers | Cross-sell, upsell, and reinforce loyalty benefits. |
| Potential Loyalists | Encourage the next purchase and category expansion. |
| New Customers | Use onboarding and second-purchase activation. |
| Promising | Use relevant reminders and repeat-purchase incentives. |
| Need Attention | Test targeted re-engagement with controlled cost. |
| At Risk | Prioritize evidence-based reactivation because historical value remains meaningful. |
| Hibernating | Use selective, low-cost reactivation tests. |
| Lost | Limit activity to low-cost win-back testing or suppression experiments. |

These actions are strategic hypotheses derived from observed segment behavior, not causal guarantees.

## Limitations

- Anonymous revenue, 13.08% of merchandise-sales revenue, cannot be assigned to customers and is excluded.
- Scores are relative to this observation window and must be rebuilt as the reference date advances.
- Preserved duplicate transactions and extreme high-value customers remain under the approved governance policy.
- Monetary measures revenue, not profit, margin, or customer lifetime value.
- RFM describes historical behavior and does not establish why customers behave differently or guarantee response to an action.

