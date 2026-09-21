# Checkpoint 3 SQL Reconciliation

## Result

Overall SQL foundation status: PASS

Instance khalez_zidan (localhost) was accessed with Windows Authentication. Database OnlineRetailAnalytics and schemas raw, staging, and analytics were created without changing server configuration.

## Table and dimension counts

| Object | Actual | Expected | Status |
|---|---:|---:|:---:|
| raw.OnlineRetailTransaction | 1,044,848 | 1,044,848 | PASS |
| staging.TransactionCanonical | 1,044,848 | 1,044,848 | PASS |
| analytics.FactTransaction | 1,044,848 | 1,044,848 | PASS |
| analytics.DimDate | 739 | 739 | PASS |
| analytics.DimCustomer | 5,942 | 5,942 | PASS |
| analytics.DimProduct | 5,131 | 5,131 governed source | PASS |
| analytics.DimCountry | 43 | 43 | PASS |

## Approved baseline reconciliation

| Metric | Actual | Expected | Status |
|---|---:|---:|:---:|
| MERCHANDISE_SALE rows | 1,015,091 | 1,015,091 | PASS |
| CUSTOMER_CANCELLATION rows | 17,974 | 17,974 | PASS |
| NON_MERCHANDISE rows | 5,719 | 5,719 | PASS |
| OPERATIONAL_STOCK_ADJUSTMENT rows | 3,392 | 3,392 | PASS |
| ZERO_PRICE_MERCHANDISE rows | 2,582 | 2,582 | PASS |
| ACCOUNTING_ADJUSTMENT rows | 73 | 73 | PASS |
| TEST_RECORD rows | 17 | 17 | PASS |
| DQ_REVIEW rows | 0 | 0 | PASS |
| MERCHANDISE_SALE LineAmount | 19,701,685.507 | 19,701,685.507 | PASS |
| CUSTOMER_CANCELLATION absolute LineAmount | 719,692.94 | 719,692.94 | PASS |
| Known-customer rows | 809,561 | 809,561 | PASS |
| Unknown-customer rows | 235,287 | 235,287 | PASS |
| Duplicate-extra flags | 11,812 | 11,812 | PASS |
| Eligible sales distinct invoices | 39,519 | 39,519 | PASS |
| Known distinct Customer IDs | 5,942 | 5,942 | PASS |

Official totals retain duplicate-flagged rows under the approved policy.

## Integrity validation

| Test | Result |
|---|---:|
| Broken Date relationships | 0 |
| Broken Product relationships | 0 |
| Broken Country relationships | 0 |
| Known customers with null CustomerKey | 0 |
| Unknown customers with populated CustomerKey | 0 |
| Duplicate Date business keys | 0 |
| Duplicate Customer business keys | 0 |
| Duplicate Product business keys | 0 |
| Duplicate Country business keys | 0 |
| Staging rows missing from fact | 0 |
| Fact rows after dimension joins | 1,044,848 |
| StockCodes with inconsistent ItemClass | 0 |
| Representative product-description mismatches | 0 |

No row multiplication or artificial row loss occurred.

## Documented review findings

- The governed canonical Parquet contains 5,131 uppercase normalized StockCodes, while the earlier trim-only baseline was 5,304. The 173-code difference results from the approved uppercase normalization. DimProduct correctly follows the governed SQL source at 5,131.
- 1,188 StockCodes have multiple normalized descriptions. The deterministic most-frequent-description rule, with ascending-description tie-break, was applied and independently validated.

No failed validation metrics remain. Full machine-readable evidence is stored in outputs/checkpoint3_sql_reconciliation.json.
