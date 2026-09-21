# Data Dictionary

| Column | Observed role | Notes |
|---|---|---|
| Invoice | Transaction document identifier | `C` prefix occurs but is not classified in this checkpoint. |
| StockCode | Item or charge code | Mixed numeric/text values; special non-merchandise codes exist. |
| Description | Item/activity description | 4,275 canonical rows are missing; whitespace variants exist. |
| Quantity | Signed transaction quantity | Negative values are not assumed to be customer returns. |
| InvoiceDate | Transaction timestamp | Drives the approved structural overlap rule. |
| Price | Unit price in source currency | Includes zero and five negative-price rows. |
| Customer ID | Customer identifier | 235,287 canonical rows are missing. |
| Country | Transaction country/market label | 43 distinct non-missing values. |

This dictionary describes source fields only; it does not introduce cleaning or business classifications.

