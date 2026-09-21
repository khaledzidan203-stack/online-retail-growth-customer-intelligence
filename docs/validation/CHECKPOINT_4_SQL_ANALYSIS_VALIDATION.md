# Checkpoint 4 SQL Analysis Validation

## Result

Overall status: PASS

| Required baseline | Actual | Expected | Status |
|---|---:|---:|:---:|
| Sales Revenue | 19,701,685.507 | 19,701,685.507 | PASS |
| Sales eligible rows | 1,015,091 | 1,015,091 | PASS |
| Sales eligible Orders | 39,519 | 39,519 | PASS |
| Cancellation Value | 719,692.94 | 719,692.94 | PASS |
| Cancellation eligible rows | 17,974 | 17,974 | PASS |
| Known Customer model population | 5,942 | 5,942 | PASS |

## Population and aggregation controls

| Control | Result |
|---|---:|
| Non-merchandise products in product ranking | 0 |
| Missing Customer IDs in customer KPI view | 0 |
| Operational adjustments in cancellation population | 0 |
| Monthly revenue difference from overall | 0 |
| Monthly cancellation-value difference from overall | 0 |
| Country revenue difference from overall | 0 |
| Country cancellation-value difference from overall | 0 |
| Product revenue difference from merchandise sales | 0 |
| Customer revenue difference from known-customer sales | 0 |
| One-time plus repeat customer difference from sales customers | 0 |

Known-customer merchandise revenue is 17,125,672.047. Total merchandise revenue is higher by 2,576,013.46 because eligible sales with missing Customer ID remain in official sales totals but are excluded from customer analysis. SQL independently reconciles this difference to the missing-customer sales rows.

## Governed rate definitions

Cancellation Value Rate uses:

Absolute Cancellation Value / (Merchandise Sales Revenue + Absolute Cancellation Value)

Country cancellation-rate rankings require at least 100 eligible sales orders. Operational stock adjustments are never included as customer cancellations.

## Time comparability

December 2009 and December 2011 are partial periods. Direct full-calendar-year comparison is not approved. The documented like-for-like comparison uses January 1 through December 9 for both 2010 and 2011.

## Output controls

Only concise aggregates were exported: one KPI row, 25 monthly rows, compact time-grain results, top-100 product and customer tables, 43 country rows, and 25 monthly cancellation rows. No detailed million-row output was created.

Machine-readable validation and headline evidence is stored in outputs/checkpoint4_sql_analysis.json.
