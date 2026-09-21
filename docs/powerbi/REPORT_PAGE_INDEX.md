# Power BI Report Page 01 — INDEX

## Purpose

`INDEX` is the report Home and navigation center for the Online Retail Growth & Customer Intelligence analytical report. It contains no analytical visuals, KPI cards, charts, slicers, or semantic-model bindings.

## Title Area

- Title: `Online Retail Growth & Customer Intelligence`
- Subtitle: `Interactive Analytics Portfolio`
- Implementation: two native Power BI textbox visuals using basic readable defaults.

## Navigation Layout

Nine native `actionButton` visuals are arranged in a centered 3-column × 3-row grid on the 1920 × 1080 canvas. Every button is 420 × 150 pixels, with consistent horizontal and vertical spacing.

| Row | Column 1 | Column 2 | Column 3 |
|---|---|---|---|
| 1 | Executive Overview | Sales Performance | Customer Intelligence |
| 2 | RFM Segmentation | Cohort & Retention | Product Performance |
| 3 | Market Analysis | Cancellations & Adjustments | Data Quality |

Each button has:

- Action enabled.
- Action type `PageNavigation`.
- `navigationSection` set to the corresponding report-page identifier.
- No semantic query or data binding.

## Destination Pages

The following destination pages exist solely to make navigation valid. They are intentionally empty and contain no visuals:

1. Executive Overview
2. Sales Performance
3. Customer Intelligence
4. RFM Segmentation
5. Cohort & Retention
6. Product Performance
7. Market Analysis
8. Cancellations & Adjustments
9. Data Quality

## Future Home Button Standard

Every future analytical page must contain exactly one native Home button configured as follows:

- Visual type: native Power BI button (`actionButton`).
- Action: On.
- Type: Page Navigation.
- Destination: `INDEX`.

Home buttons must be added only when the corresponding analytical page is explicitly authorized for construction.

## Validation

| Check | Result |
|---|---:|
| INDEX page exists | PASS |
| Native navigation buttons | 9 |
| Valid destinations | 9 |
| Broken navigation targets | 0 |
| Analytical visuals on INDEX | 0 |
| Slicers on INDEX | 0 |
| Destination-page visuals | 0 |
| Invalid JSON | 0 |
| Broken semantic bindings | 0 |
| Navigation errors | 0 |
| Visuals outside canvas | 0 |
| PBIR schema validation | PASS — 23 files, 0 errors |
| Semantic measures | Unchanged at 50 |
| Semantic relationships | Unchanged at 7 |

The page uses the existing Power BI base theme with no custom theme, decorative background, icon set, or branding treatment.
