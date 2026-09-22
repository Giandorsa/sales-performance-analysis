# Sales performance dashboard

## Status

This folder contains the [original dashboard screenshot](dashboard_screenshot.png), the V2 model guide, measures and theme. No editable `.pbix` or `.pbip` report is available; these assets are not a completed interactive dashboard.

## Model

1. Run `python main.py prepare` and import `data/processed/sales_processed.csv` as `Sales`.
2. Set `order_date` to Date, monetary columns to Fixed decimal number, IDs to Text and `is_returned` to Whole number.
3. Create the `Calendar` calculated table in `measures.dax`, mark it as a date table and relate `Calendar[Date]` (one) to `Sales[order_date]` (many), with single-direction filtering.
4. Create each measure separately. Import `theme.json` using View > Themes > Browse for themes.
5. Use the reporting CSVs only for reconciliation. Do not join aggregate reports to the fact table. Distinct customers must be calculated from `Sales`, not summed across months or categories.

## Executive overview

Use a 16:9 white canvas, Segoe UI, generous spacing and dark teal (`#264653`) for revenue. Reserve coral (`#e76f51`) for returns. These colors follow Project 02's existing charts.

- Header: Sales performance, selected date range and category / region slicers.
- First row: Net revenue (estimated), Orders, Net AOV, Customers, Return rate.
- Middle row: Monthly net revenue trend; Net revenue by category.
- Bottom row: Net revenue by region; Gross sales to net revenue bridge.
- Second page: Top 10 products and customers by net revenue, plus orders, returns and net AOV; discount-level performance table.

Use sorted horizontal bars, light gridlines and explicit units. Format monetary measures as USD (for example, `US$ #,##0.00`) and include the report note: "Synthetic data; USD assumed for presentation; no currency conversion applied." Show return rate as a percentage. Label September 2023 and September 2025 as partial months. Use `monthly_performance.csv` in a separate, disconnected reconciliation page to review MoM and YoY values; blanks mean the comparison is unavailable. Do not replace these blanks with zero or publish unguarded date-shift comparisons.

## Validation

With no filters: 34,500 orders, 7,903 customers, 5,476,537.08 estimated net revenue, 158.74 net AOV and 5.52% return rate. The revenue bridge is 6,173,811.37 gross sales minus 308,518.32 discounts minus 388,755.97 returned revenue.

Net revenue assumes full refunds and attributes returns to the original order date. No refund amounts or return dates are available. The old screenshot uses revenue before returns and should not be presented as V2.
