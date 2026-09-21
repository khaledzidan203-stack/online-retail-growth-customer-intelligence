# Data Discovery

## Source structure

The workbook contains the expected two sheets and eight columns. Reproduced row counts are 525,461 for `Year 2009-2010` and 541,910 for `Year 2010-2011`, totaling 1,067,371.

## Structural overlap

The first sheet contains 22,523 rows dated on or after 2010-12-01. Their full-row multiset matches 22,523 rows in the second sheet and contains 1,088 distinct invoices.

The temporary canonical view retains first-sheet rows before 2010-12-01 plus every second-sheet row. It contains 1,044,848 rows spanning 2009-12-01 07:45 to 2011-12-09 12:50. No general deduplication was performed and no row-level dataset was exported.

## Reproduced canonical metrics

| Metric | Actual | Expected | Status |
|---|---:|---:|:---:|
| Distinct invoices | 53,628 | 53,628 | PASS |
| Distinct StockCodes (raw exact) | 5,305 | 5,305 | PASS |
| Distinct StockCodes (trimmed) | 5,304 | 5,304 | PASS |
| Distinct descriptions (raw exact) | 5,698 | 5,698 | PASS |
| Distinct descriptions (trimmed) | 5,655 | 5,655 | PASS |
| Distinct known Customer IDs | 5,942 | 5,942 | PASS |
| Countries | 43 | 43 | PASS |
| Missing Customer ID | 235,287 | 235,287 | PASS |
| Missing Description | 4,275 | 4,275 | PASS |
| Positive / negative / zero quantity | 1,022,291 / 22,557 / 0 | same | PASS |
| C-prefixed rows / distinct C invoices | 19,165 / 8,292 | same | PASS |
| Negative quantity without C prefix | 3,393 | 3,393 | PASS |
| Positive / zero / negative price | 1,038,819 / 6,024 / 5 | same | PASS |
| Exact repeated rows beyond first | 11,812 | 11,812 | PASS |
| Rows participating in exact duplicate groups | 22,813 | 22,813 | PASS |
| Exact duplicate groups | 11,001 | 11,001 | PASS |

Raw and whitespace-trimmed distinct counts are reported separately. The canonical view and raw source were not altered.
