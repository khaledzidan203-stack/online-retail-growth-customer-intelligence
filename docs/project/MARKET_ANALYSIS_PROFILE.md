# Market Analysis — source profile

Read-only SQL Server profile of `OnlineRetailAnalytics.analytics.vw_CountryPerformance`, reconciled to governed FactTransaction eligibility. Profile date: 2026-09-21. No SQL or DAX objects changed.

## Scope and concentration

43 country labels; 1,044,848 fact rows; 2009-12-01–2011-12-09. Full-period static baseline, not a response to report slicers.

Sales Revenue: 19,701,685.51; Orders: 39,519; distinct eligible known customers: 5852; Units Sold: 11,221,960; Cancellation Value: 719,692.94.

UK shares: revenue 85.56%; orders 91.57%; known customers 91.15%; units 82.06%. UK cancellation value 635,249.66 (88.27% of all cancellation value), rate 3.63%.

- Top 1 country revenue share: 85.56%.
- Top 3 country revenue share: 91.52%.
- Top 5 country revenue share: 95.05%.
- Top 10 country revenue share: 97.65%.

## Country metrics (revenue descending)

| Country | Sales Revenue | Revenue share | Orders | Known customers | AOV | Units | Cancellation Value | Cancellation Rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| United Kingdom | 16,857,062.01 | 85.56% | 36187 | 5334 | 465.83 | 9,209,210 | 635,249.66 | 3.63% |
| EIRE | 623,795.85 | 3.17% | 581 | 3 | 1,073.66 | 336,323 | 20,388.75 | 3.17% |
| Netherlands | 549,775.06 | 2.79% | 216 | 22 | 2,545.25 | 383,626 | 3,677.98 | 0.66% |
| Germany | 383,847.67 | 1.95% | 753 | 107 | 509.76 | 223,303 | 8,715.49 | 2.22% |
| France | 311,288.38 | 1.58% | 598 | 93 | 520.55 | 270,779 | 17,662.04 | 5.37% |
| Australia | 167,867.51 | 0.85% | 89 | 15 | 1,886.15 | 103,763 | 1,517.86 | 0.90% |
| Spain | 97,818.07 | 0.50% | 144 | 38 | 679.29 | 50,018 | 12,955.19 | 11.70% |
| Switzerland | 94,046.89 | 0.48% | 85 | 22 | 1,106.43 | 52,624 | 1,106.53 | 1.16% |
| Sweden | 86,353.04 | 0.44% | 99 | 19 | 872.25 | 88,554 | 1,973.97 | 2.23% |
| Denmark | 67,422.69 | 0.34% | 42 | 12 | 1,605.3 | 237,406 | 4,067.1 | 5.69% |
| Belgium | 57,012.67 | 0.29% | 143 | 29 | 398.69 | 34,353 | 394.28 | 0.69% |
| Portugal | 47,406.87 | 0.24% | 85 | 23 | 557.73 | 27,565 | 630.28 | 1.31% |
| Channel Islands | 44,040.23 | 0.22% | 54 | 13 | 815.56 | 21,395 | 2,188.52 | 4.73% |
| Japan | 43,023.91 | 0.22% | 33 | 10 | 1,303.75 | 31,643 | 3,277.14 | 7.08% |
| Norway | 38,575.36 | 0.20% | 39 | 12 | 989.11 | 23,556 | 161.68 | 0.42% |
| Italy | 28,951.95 | 0.15% | 59 | 17 | 490.71 | 15,260 | 710.7 | 2.40% |
| Finland | 25,180.1 | 0.13% | 54 | 13 | 466.3 | 14,265 | 90.44 | 0.36% |
| Cyprus | 24,614.44 | 0.12% | 35 | 11 | 703.27 | 10,982 | 496.7 | 1.98% |
| Austria | 20,297.01 | 0.10% | 40 | 13 | 507.43 | 11,499 | 225.41 | 1.10% |
| Greece | 18,711.19 | 0.09% | 18 | 5 | 1,039.51 | 7,716 | 50.7 | 0.27% |
| Hong Kong | 13,875.25 | 0.07% | 9 | 0 | 1,541.69 | 7,074 | 10.95 | 0.08% |
| Singapore | 13,158.16 | 0.07% | 8 | 1 | 1,644.77 | 6,987 | 0 | 0.00% |
| Israel | 11,334.66 | 0.06% | 10 | 4 | 1,133.47 | 5,541 | 227.44 | 1.97% |
| Unspecified | 10,936.01 | 0.06% | 24 | 6 | 455.67 | 6,734 | 22 | 0.20% |
| United Arab Emirates | 10,273.23 | 0.05% | 12 | 4 | 856.1 | 7,316 | 645.08 | 5.91% |
| Poland | 10,214.29 | 0.05% | 28 | 6 | 364.8 | 5,677 | 374.36 | 3.54% |
| USA | 7,920.01 | 0.04% | 16 | 8 | 495 | 5,259 | 2,080.32 | 20.80% |
| Iceland | 4,921.53 | 0.02% | 8 | 1 | 615.19 | 2,967 | 0 | 0.00% |
| Lithuania | 4,892.68 | 0.02% | 6 | 1 | 815.45 | 2,306 | 0 | 0.00% |
| Malta | 4,757.34 | 0.02% | 7 | 2 | 679.62 | 2,505 | 90.12 | 1.86% |
| Canada | 4,332.1 | 0.02% | 7 | 5 | 618.87 | 3,656 | 0 | 0.00% |
| RSA | 3,369.03 | 0.02% | 3 | 2 | 1,123.01 | 1,969 | 0 | 0.00% |
| Bahrain | 3,109.79 | 0.02% | 10 | 2 | 310.98 | 1,339 | 248.24 | 7.39% |
| Thailand | 3,070.54 | 0.02% | 2 | 1 | 1,535.27 | 2,552 | 0 | 0.00% |
| Lebanon | 1,905.58 | 0.01% | 2 | 1 | 952.79 | 458 | 0 | 0.00% |
| Brazil | 1,411.87 | 0.01% | 2 | 2 | 705.94 | 545 | 0 | 0.00% |
| Bermuda | 1,253.14 | 0.01% | 1 | 0 | 1,253.14 | 2,798 | 0 | 0.00% |
| European Community | 1,159.25 | 0.01% | 3 | 1 | 386.42 | 490 | 8.5 | 0.73% |
| Korea | 1,118.51 | 0.01% | 2 | 2 | 559.26 | 700 | 168.69 | 13.11% |
| Czech Republic | 786.74 | 0.00% | 2 | 1 | 393.37 | 670 | 115.02 | 12.76% |
| West Indies | 536.41 | 0.00% | 1 | 1 | 536.41 | 395 | 0 | 0.00% |
| Saudi Arabia | 145.92 | 0.00% | 1 | 1 | 145.92 | 80 | 14.75 | 9.18% |
| Nigeria | 112.57 | 0.00% | 1 | 1 | 112.57 | 102 | 147.05 | 56.64% |

## Top ten overall

1. United Kingdom: 16,857,062.01
2. EIRE: 623,795.85
3. Netherlands: 549,775.06
4. Germany: 383,847.67
5. France: 311,288.38
6. Australia: 167,867.51
7. Spain: 97,818.07
8. Switzerland: 94,046.89
9. Sweden: 86,353.04
10. Denmark: 67,422.69

## Top ten non-UK

1. EIRE: 623,795.85
2. Netherlands: 549,775.06
3. Germany: 383,847.67
4. France: 311,288.38
5. Australia: 167,867.51
6. Spain: 97,818.07
7. Switzerland: 94,046.89
8. Sweden: 86,353.04
9. Denmark: 67,422.69
10. Belgium: 57,012.67

## Interpretation, cancellation risk and data quality

- UK dominates scale. Show UK in overall ranking, with a separate explicitly labelled non-UK ranking, never a page-wide exclusion.
- EIRE has 581 orders but only three known customers; Netherlands has 216 orders, 22 known customers and AOV 2,545.25. Germany has 107 known customers. High market revenue does not establish broad customer depth.
- Nigeria has a 56.64% cancellation rate but only one sales order; Korea and Czech Republic have two orders each and elevated rates. USA has 16 orders; Saudi Arabia one. Do not rank all markets solely by unqualified rate.
- Spain has 144 orders and cancellation value 12,955.19 (11.70% rate): a more material risk signal. Absolute cancellation ranking plus rate and scale in the table provides context without a fabricated threshold.
- Hong Kong and Bermuda have zero known customers despite sales. Anonymous Sales Revenue across the model is 2,576,013.46 (13.08% of revenue). Known customers exclude anonymous identifiers; revenue/orders include eligible anonymous transactions.
- Country is the recorded transaction market, not a proven customer residence. Distinct customer counts across markets are not additive; UK customer share uses the global distinct denominator 5852.
- Preserve labels such as EIRE, Unspecified and European Community; do not remap or impute them.
- Revenue and units use IsSalesEligible; customers use IsCustomerAnalyticsEligible; cancellations use absolute IsCancellationEligible amounts. Cancellation Value Rate = Cancellation Value / (Sales Revenue + Cancellation Value), not a net-sales measure.
- 2009 and 2011 are partial periods; no profitability, market-size or causal claims are supported. Governed preserved-row logic remains unchanged.
- Recomputed ratios use unrounded source amounts; the SQL view's rounded ratio display may differ at trailing decimal places.

## Selected page design

Five governed KPIs; Top 5 overall revenue; Top 5 non-UK revenue; Top 5 cancellation value; full-width eight-column market economics table sorted by revenue. A labelled static full-period concentration note complements dynamic filtered visuals. Table scrolling across all 43 labels is intentional.

