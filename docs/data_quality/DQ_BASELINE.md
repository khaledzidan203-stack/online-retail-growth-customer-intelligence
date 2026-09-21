# Data Quality Baseline

## Validated observations

- Canonical structural rows: 1,044,848.
- Missing Customer ID: 235,287 rows.
- Missing Description: 4,275 rows.
- Quantity: 1,022,291 positive, 22,557 negative, 0 zero.
- Invoice prefix: 19,165 `C` rows across 8,292 invoices.
- Negative quantity without `C`: 3,393 rows.
- Price: 1,038,819 positive, 6,024 zero, 5 negative.
- Exact repeated rows beyond the first occurrence: 11,812.
- Rows participating in exact duplicate groups: 22,813.
- Exact duplicate groups: 11,001.

## Review items

- Raw exact text counts are StockCode 5,305 and Description 5,698; whitespace-trimmed counts are 5,304 and 5,655 respectively.
- Exact duplicates remain present by approved policy; official totals preserve them and duplicate impact is reported as a sensitivity.
- Negative quantities, special codes, adjustments, missing identifiers, and zero-price activity require later governed classification.

No rows were cleaned, reclassified, deduplicated, or exported in this checkpoint.
