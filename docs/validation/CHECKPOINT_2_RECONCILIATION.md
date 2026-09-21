# Checkpoint 2 Reconciliation

## Result

Overall status: PASS

| Reconciliation | Result |
|---|:---:|
| Canonical rows = 1,044,848 | PASS |
| TransactionClass counts sum to canonical rows | PASS |
| ItemClass counts sum to canonical rows | PASS |
| Known + unknown customer rows = canonical rows | PASS |
| Duplicate-after-first + non-duplicate rows = canonical rows | PASS |
| Duplicate extra rows = 11,812 | PASS |
| Duplicate participating rows = 22,813 | PASS |
| Duplicate groups = 11,001 | PASS |

## Transaction classes

| TransactionClass | Rows |
|---|---:|
| ACCOUNTING_ADJUSTMENT | 73 |
| CUSTOMER_CANCELLATION | 17,974 |
| MERCHANDISE_SALE | 1,015,091 |
| NON_MERCHANDISE | 5,719 |
| OPERATIONAL_STOCK_ADJUSTMENT | 3,392 |
| TEST_RECORD | 17 |
| ZERO_PRICE_MERCHANDISE | 2,582 |

## Eligibility and value

- Sales eligible: 1,015,091 rows; LineAmount 19,701,685.507.
- Customer analytics eligible: 788,209 rows.
- Cancellation eligible: 17,974 rows; absolute LineAmount 719,692.94.
- Operational stock adjustments: 3,392 rows; LineAmount 0.0.
- Known customer: 809,561 rows; unknown customer: 235,287 rows.
- DQ_REVIEW: 0 rows.

## Duplicate impact

| TransactionClass | Extra rows | Quantity | LineAmount |
|---|---:|---:|---:|
| CUSTOMER_CANCELLATION | 59 | -2,142 | -3,230.37 |
| MERCHANDISE_SALE | 11,731 | 33,896 | 57,092.82 |
| NON_MERCHANDISE | 12 | 300 | 365.97 |
| ZERO_PRICE_MERCHANDISE | 10 | 11 | 0.00 |

Retaining duplicate-after-first rows increases reported merchandise sales revenue by 57,092.82. It does not change the eligible distinct order count: 39,519 with or without those extra rows.

## Edge cases and limitations

- Invoice C496350 / StockCode M resolves to MANUAL and NON_MERCHANDISE under precedence.
- The remaining negative non-C row is StockCode GIFT and resolves to GIFT_VOUCHER / NON_MERCHANDISE; the other 3,392 become operational adjustments.
- All five negative-price rows resolve to ACCOUNTING_ADJUSTMENT.
- No rows were deleted, imputed, or rounded.
- Duplicate rows are preserved by approved policy; any later review of merchandise-default special codes remains open.
