# Python EDA Baseline

## Independent SQL reconciliation

Python independently aggregated SQL-sourced order, customer, and cancellation populations. All 11 required KPI comparisons pass, including sales revenue 19,701,685.507, 11,221,960 units, 39,519 orders, 5,852 sales-known customers, 17,125,672.047 known-customer revenue, 4,234 repeat customers, 1,618 one-time customers, and 719,692.94 cancellation value.

## Order behavior

Order revenue is strongly right-skewed. Mean revenue is 498.54 versus a median of 301.80; P95 is 1,435.08, P99 is 4,103.75, and the maximum is 168,469.60.

Order units show the same wholesale tail. Mean units are 283.96 versus a median of 149; P95 is 798, P99 is 2,224, and the maximum is 87,167. The elevated mean is therefore materially driven by high-quantity wholesale orders and should not be interpreted as a typical order.

## Customer behavior

Customer revenue has a median of 860.27 versus a mean of 2,926.46. P95 is 9,270.27, P99 is 28,675.15, and the maximum is 580,987.04.

Customers place a median of 3 orders; P95 is 20, P99 is 46, and the maximum is 373. The median observed lifespan is 223 days, while 25% of customers have a zero-day lifespan because all eligible purchases occur on one date. Among successive customer orders, median interpurchase time is 25 days, P90 is 136 days, and P99 is 369 days.

These are analytical-population characteristics only. No RFM scores, segments, cohorts, or retention measures were created.

## Product behavior

Across 4,726 merchandise products with eligible sales, median product revenue is 1,129.30, P95 is 18,067.85, P99 is 47,014.88, and the maximum is 331,084.27. Median product units are 653.5, P99 is 26,700.5, and the maximum is 106,379.

Products appear in a median of 89 orders and reach a median of 50.5 known customers. Weighted average selling price has a median of 1.96, P99 of 22.48, and maximum of 243.68. High-volume and high-value products are retained and described as distribution tails rather than errors.

## Market behavior

Country revenue is extremely concentrated: median market revenue is 13,158.16 while the United Kingdom records 16,857,062.006 and 85.56% of total revenue. Median market order count is 18 compared with 36,187 for the UK. Transaction data alone does not explain the geographic concentration.

## Anonymous-customer impact

Anonymous sales contribute 2,576,013.46 of revenue, 689,657 units, 2,922 orders, and 226,882 lines. They represent 13.08% of sales revenue and have AOV 881.59 versus 467.95 for known-customer orders. There are no mixed known/anonymous invoices.

RFM, cohort, and retention analysis must therefore use the smaller known-customer population and cannot represent anonymous sales behavior without unsupported identity imputation.

## Duplicate sensitivity

Official KPIs preserve duplicate-flagged rows. Excluding duplicate-after-first rows only as a sensitivity would reduce:

- Revenue by 57,092.82, approximately 0.290%.
- Units by 33,896, approximately 0.302%.
- AOV by 1.44, approximately 0.290%.
- Cancellation value by 3,230.37, approximately 0.449%.

Distinct eligible orders remain 39,519. These small but measurable effects do not change the approved duplicate policy.

## StockCode 23843 / Customer 16446

The event consists of a merchandise sale and cancellation twelve minutes apart on 2011-12-09:

- Invoice 581483 at 09:15: quantity 80,995, unit price 2.08, LineAmount 168,469.60.
- Invoice C581484 at 09:27: quantity -80,995, unit price 2.08, LineAmount -168,469.60.

The cancellation is one line on one cancellation invoice. It contributes 23.41% of total cancellation value and 96.75% of December 2011 cancellation value. Removing only this cancellation for sensitivity would reduce total cancellation value to 551,223.34 and the value rate from 3.5242% to 2.7217%.

December 2011 falls from 174,126.76 to 5,657.16 without this event and is no longer the highest cancellation month; January 2011 becomes highest at 91,526.30. The source record remains in every official KPI.

## Forecasting readiness

Status: CONDITIONAL

The calendar contains all 739 expected dates, but 135 days have zero merchandise revenue. There are 106 weekly observations. Daily lag-7 autocorrelation is 0.641, lag-28 is 0.516, and lag-365 is 0.451, providing evidence of recurring structure. The maximum daily revenue is 198,114.26, 2.30 times P99.

The approximately two-year history, partial December boundaries, wholesale spikes, and large cancellation anomaly require robust outlier handling rules, rolling-origin backtesting, and careful training-window selection before forecasting. No forecast was created.

## Questions carried forward

- How should the future RFM observation date and customer eligibility window be governed?
- How should one-time customers be handled in frequency and recency interpretation?
- Should duplicate sensitivity be shown alongside, but never substituted for, official RFM monetary values?
- How should the 13.08% anonymous revenue share be disclosed beside customer-only analyses?
- How should the documented 23843/16446 event be presented in later cancellation reporting?
