# Customer Intelligence

## Purpose
Customer-level performance analysis using the governed fact/dimension model.

## Controls
- **Year:** `analytics DimDate[Year]`
- **Country:** `analytics DimCountry[Country]`

Both slicers filter all KPI cards and customer visuals on this page. The native HOME button navigates to INDEX.

## KPI cards
Sales Customers; Repeat Customers; Repeat Customer Rate; Revenue per Known Customer; Orders per Known Customer; and Known Customer Revenue.

## Visuals
- **Repeat vs One-Time Customers:** repeat and one-time customer counts.
- **Known vs Anonymous Sales Revenue:** known and anonymous sales-revenue comparison.
- **Customer Value vs Purchase Frequency:** `analytics DimCustomer[CustomerID]` with `[Orders]` on X and `[Sales Revenue]` on Y. Tooltip: customer ID, Orders, Sales Revenue, and Average Order Value.
- **Top Customers by Revenue:** Top 10 `analytics DimCustomer[CustomerID]`, descending by `[Sales Revenue]`. Tooltip: customer ID, Sales Revenue, Orders, and Average Order Value.

The value/frequency and ranking visuals use the governed fact/dimension model, not the CustomerRFM snapshot, so they respond to both Year and Country.

## Validation
No measures, relationships, SQL, or other report pages were changed. The two corrected visuals use existing governed measures and valid page-level default slicer interactions.
