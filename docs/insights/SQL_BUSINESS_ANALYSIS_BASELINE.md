# SQL Business Analysis Baseline

## Core performance

- Merchandise sales revenue is 19,701,685.507 from 39,519 orders and 11,221,960 units.
- Average order value is 498.54 and average units per order is 283.96.
- 5,852 customers have eligible merchandise sales. Their revenue is 17,125,672.047, or 2,576,013.46 below total merchandise revenue because missing Customer IDs are not assigned to fabricated customers.
- Sales customers include 1,618 one-time and 4,234 repeat customers, producing a 72.35% repeat-customer rate and average purchase frequency of 6.25 orders.

## Time baseline

Calendar totals are 801,102.97 for partial December 2009, 9,407,081.244 for full 2010, and 9,493,501.293 for 2011 through December 9. These calendar totals are not directly comparable as full years.

For the common January 1–December 9 window, sales revenue rose from 9,038,376.034 in 2010 to 9,493,501.293 in 2011, approximately 5.0%. Orders fell from 18,910 to 18,223 and units from 5,398,833 to 5,218,354, while cancellation value rose from 228,270.53 to 461,116.32.

November 2011 is the highest-revenue month at 1,457,745.53. The highest-revenue quarter is 2010 Q4 at 3,311,629.562, although quarter comparisons involving 2011 Q4 must account for the December 9 endpoint. Thursday is the highest-revenue weekday and 12:00 is the highest-revenue hour across the full period.

## Product baseline

The leading revenue product is StockCode 22423, REGENCY CAKESTAND 3 TIER, with 331,084.27. StockCode 84077 leads units with 106,379. StockCode 85123A leads both orders (5,464) and known customers (1,490).

Product revenue is relatively dispersed: the top 10 products contribute 8.03%, the top 20 contribute 11.49%, and the top 100 contribute 29.43%. It takes 284 products to reach 50% of revenue, 1,031 to reach 80%, and 1,685 to reach 90%.

StockCode 23843 records 168,469.60 from one sale and the same value as a cancellation. This is an important concentration and time-rate sensitivity, not a basis for silently removing the governed records.

## Customer baseline

Customer 18102 leads known-customer revenue at 580,987.04, followed by 14646 at 526,751.52. The top 10 customers contribute 16.09% of known-customer revenue, the top 20 contribute 21.91%, and the top 100 contribute 37.55%.

It takes 260 customers to reach 50% of known-customer revenue, 1,357 to reach 80%, and 2,343 to reach 90%. Customer revenue is more concentrated than product revenue but is not dominated by only a handful of customers.

## Country and market baseline

The United Kingdom contributes 16,857,062.006, or 85.56% of merchandise revenue. Non-UK markets contribute 14.44%. The top 10 countries contribute 97.65%; one country exceeds 80%, and three countries reach 90%.

The Netherlands has the highest AOV among markets with at least 100 eligible orders at 2,545.25. The United Kingdom has the most known sales customers at 5,334. Spain has the highest cancellation value rate among markets meeting the 100-order safeguard at 11.70%.

This is a highly concentrated geographic profile, unlike the more distributed product and customer profiles.

## Cancellation baseline

Approved customer cancellations total 719,692.94 across 469,882 units and 7,406 cancellation invoices. There are 2,445 known customers with cancellations. The governed cancellation value rate is 3.5242%, using cancellation value divided by sales revenue plus cancellation value.

The United Kingdom has the highest cancellation value at 635,249.66. StockCode 23843 and customer 16446 each have 168,469.60 of cancellation value. December 2011 has the highest monthly cancellation value at 174,126.76 and a 22.05% cancellation value rate, but it is a partial month and is strongly affected by the StockCode 23843 transaction.

Operational stock adjustments are excluded from every cancellation KPI and remain separately visible in the cancellation performance view.

## Interpretation boundary

These findings are descriptive SQL baselines for later validation. They are not final business recommendations, RFM segments, cohort conclusions, forecasts, profit measures, or causal claims.
