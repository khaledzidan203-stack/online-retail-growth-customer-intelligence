# Transaction Classification

## Canonical source and lineage

The pipeline keeps Year 2009-2010 rows before 2010-12-01 and all Year 2010-2011 rows. It preserves SourceSheet and the one-based Excel SourceRowNumber (including the header row), plus raw text fields where normalization changes may matter. No questionable or duplicate record is deleted.

## Normalization

| Field | Governed rule |
|---|---|
| Invoice | Convert to text and trim surrounding whitespace. |
| StockCode | Preserve StockCodeRaw; trim and uppercase StockCode. |
| Description | Preserve DescriptionRaw; trim and collapse internal whitespace while retaining case. |
| Customer ID | Preserve numeric CustomerIDRaw; store nullable string CustomerID without .0; never impute. |
| Country | Preserve CountryRaw; trim Country without renaming values. |
| InvoiceDate | Store as datetime. |
| Quantity | Validate and store as nullable integer. |
| Price | Store as numeric without rounding. |
| LineAmount | Calculate Quantity multiplied by Price without rounding. |

## Item classes

The single mapping source is config/item_classification.json. Unmapped codes default to MERCHANDISE.

| Codes | ItemClass |
|---|---|
| POST, DOT, C2 | SHIPPING_SERVICE |
| D | DISCOUNT |
| M | MANUAL |
| BANK CHARGES, AMAZONFEE, CRUK | FINANCIAL_FEE |
| ADJUST, B | ACCOUNTING_ADJUSTMENT |
| S | SAMPLE |
| TEST001, TEST002 | TEST |
| GIFT and GIFT_0001_ prefix | GIFT_VOUCHER |

PADS and DCG* are not specially mapped and therefore remain MERCHANDISE.

## Transaction precedence

Rules are evaluated in this order:

1. ACCOUNTING_ADJUSTMENT: A-prefixed invoice or accounting-adjustment item.
2. TEST_RECORD: test item.
3. NON_MERCHANDISE: shipping, discount, manual, financial fee, sample, or gift voucher.
4. CUSTOMER_CANCELLATION: merchandise, C-prefixed invoice, and negative quantity.
5. DQ_REVIEW: merchandise, C-prefixed invoice, and non-negative quantity.
6. OPERATIONAL_STOCK_ADJUSTMENT: merchandise, negative quantity, and no C prefix.
7. ZERO_PRICE_MERCHANDISE: merchandise, positive quantity, and zero price.
8. MERCHANDISE_SALE: merchandise, positive quantity, and positive price.
9. DQ_REVIEW: any remaining record.

The cited row for invoice C496350, StockCode M, is classified MANUAL and then NON_MERCHANDISE. Non-merchandise precedence intentionally prevents it from being treated as merchandise or a customer cancellation.

## Analytical flags

- IsKnownCustomer: normalized CustomerID is present.
- IsCancellationInvoice: Invoice begins with C.
- IsMerchandise: ItemClass is MERCHANDISE.
- IsSalesEligible: TransactionClass is MERCHANDISE_SALE.
- IsCustomerAnalyticsEligible: sales eligible and customer is known.
- IsCancellationEligible: TransactionClass is CUSTOMER_CANCELLATION.
- IsZeroPrice and IsNegativePrice: direct Price tests.
- IsExactDuplicateAfterFirst: exact repetition of the eight original business columns after the structural overlap rule.

## Duplicate policy

Duplicates are retained under the approved policy because no reliable source line key proves they are erroneous. The output records whether a row participates in any exact duplicate group and its group size. Duplicate impact remains a documented sensitivity, while official analytical totals use the complete preserved population.

## Current unresolved issues

- Special merchandise-default codes such as PADS and DCG* may need later evidence-based review.
- Operational stock adjustments must not be presented as customer returns.
- Missing customers remain in the canonical population but are excluded from customer-analytics eligibility.
- No residual records currently fall into DQ_REVIEW; this is a result of the approved precedence, not a reason to remove the review rule.
