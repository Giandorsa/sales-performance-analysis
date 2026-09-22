# Sales Performance Analysis: Revenue, Returns & Commercial Trends

## Overview

This project analyzes order-level sales to explain commercial performance across categories, regions, products and customers. Python prepares validated transactions and reporting tables, SQLite supports business queries, and the Power BI assets define the reporting layer under development.

The goal is to help a commercial manager prioritize investigation of returns while monitoring sales performance through a reproducible analytical workflow.

## Business question

In this simulated business scenario, a commercial manager needs to distinguish sales booked before returns from the estimated revenue retained after refunds. The decision is where to focus a follow-up investigation: categories with the largest returned amounts, categories with the highest return frequency, or changes in monthly performance.

This is an exploratory review, not a response to a proven decline or a known operational failure. The synthetic dataset contains no business targets, return reasons or actual refund amounts.

**How much revenue remains after discounts and estimated refunds, and which categories should commercial management investigate first based on return value and frequency?**

Supporting questions are how net performance changes across complete months, how concentrated revenue is by category and region, and how observed results differ across discount levels.

## Dataset

The included `data/raw/dataset.csv` contains 34,500 orders and 7,903 customers from September 12, 2023 to September 11, 2025. Each row represents one order with one recorded product. Fields cover pricing, quantity, discount, category, region, customer and return status.

The source is [E-commerce Sales Transactions Dataset by Arif Miah on Kaggle](https://www.kaggle.com/datasets/miadul/e-commerce-sales-transactions-dataset), described by its publisher as synthetic and listed under Apache 2.0. The downloaded `ecommerce_sales_34500.csv` was compared with the included `dataset.csv`: all 34,500 rows, 17 columns and parsed values match. The local file was renamed; byte-level checksums differ.

The data simulates transactions rather than documenting a real business or a verified national market. Generic regions such as South and North do not identify a country. **USD is the presentation convention for this portfolio**, not a verified source currency; amounts are displayed without exchange-rate conversion.

## Stack

- Python: Pandas and NumPy
- SQL and SQLite
- Power BI for interactive reporting
- Pytest for business-rule checks
- Git and GitHub for version control and documentation

## Workflow

1. Read source orders and remove exact duplicate rows.
2. Validate required fields, order uniqueness, dates, numeric ranges and return flags.
3. Calculate gross sales, discounts, revenue before returns and estimated net revenue.
4. Build monthly, category, region, product, customer and discount reporting tables.
5. Export CSV files, a validation summary and a SQLite database.
6. Run named SQL analyses and reconcile the Power BI measures against their results.

## Initial findings

All monetary figures below are presented in USD under the convention described above.

- Revenue before returns totals **5,865,293.05**. Assuming full refunds on returned orders reduces it by **388,755.97** to **5,476,537.08** estimated net revenue.
- **1,903 orders were returned (5.52%)**. Net revenue per recorded order is **158.74**, compared with **170.01** before returns.
- Returned revenue represents **6.63% of revenue before returns**. This differs from the order return rate because orders have different monetary values.
- Discounts total **308,518.32**, or **5.00% of gross revenue**. This measures the recorded reduction from list-price sales; it does not show whether discounts generated incremental demand.
- Electronics contributes **3,074,107.12**, or **56.1% of net revenue**. Its returned revenue is **245,099.38**, making it the largest source of revenue exposed to returns.
- Fashion has the highest category return rate at **8.28%**, compared with **7.30%** for Electronics. These categories warrant investigation for different reasons: return frequency versus monetary impact.
- South leads regional net revenue at **1,203,853.24**, closely followed by North at **1,192,986.82**.
- December 2024 has the highest monthly net revenue at **253,106.85**. A single peak does not establish seasonality.

Electronics accounts for **63.05% of all returned revenue**, making it the first category to investigate by monetary exposure. Fashion is the first category to investigate by return frequency. This is a prioritization of analytical follow-up, not an estimate of recoverable revenue or evidence of poor product quality.

### Suggested business actions

| Priority | Evidence | Suggested investigation | Additional evidence needed |
| --- | --- | --- | --- |
| Electronics: monetary exposure | USD 245,099.38 returned; 63.05% of total returned revenue | Review the orders contributing most returned value and compare patterns within the category | Actual refund amounts, return reasons, stable product master data |
| Fashion: return frequency | 8.28% of orders returned versus 5.52% overall | Check whether the rate persists across months and product groups | Return reasons, product attributes, delivery and quality records |
| Discounts: commercial trade-off | USD 308,518.32 in recorded discounts | Compare category mix, net AOV and returns within discount levels before proposing pricing changes | Promotion dates, unit costs and a credible comparison group |
| Monthly performance: monitoring | December 2024 leads net revenue; boundary months are partial | Compare complete months and separate order volume from net AOV changes | Targets and a longer history before inferring seasonality |

These are proposed actions for the simulated scenario. The analysis does not establish why returns occurred, whether discounts caused sales, or how much a policy change would save. No performance target or expected uplift is invented.

## Project structure

```text
data/raw/             Included source CSV
data/processed/       Generated CSV reports, validation audit and sales.db
src/                  Data cleaning, business metrics and execution workflows
sql/queries.sql       All business analyses in one SQL worksheet
powerbi/              Dashboard screenshot, DAX measures and theme
tests/                Business-rule and reconciliation checks
main.py               Main command line entry point
```

### Repository guide

| If you want to inspect... | Go to |
| --- | --- |
| Commands and execution order | `main.py` and `src/workflows.py` |
| Cleaning, validation and revenue definitions | `src/data_cleaning.py` |
| Aggregation and monthly comparisons | `src/sales_reporting.py` |
| CSV exports, SQLite persistence and SQL execution | `src/workflows.py` |
| Business queries | `sql/queries.sql` |
| Dashboard assets and measures | `powerbi/` |
| Core business-rule checks | `tests/` |

The Python code uses three functional modules: `data_cleaning.py` validates orders and defines order-level amounts, `sales_reporting.py` aggregates business metrics, and `workflows.py` coordinates file exports, SQLite storage and SQL execution. `src/__init__.py` marks the package and contains no execution logic. Generated `__pycache__/` folders are ignored by Git; they can be deleted and Python recreates them when needed.

## How to run

Use Python 3.10 or later. From the repository root:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS / Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py all
python main.py sql --query sales_overview
python main.py sql --query monthly_performance
python main.py sql --query all
python -m pytest tests
```

Use `python main.py prepare` to rebuild the data without printing all analyses. All data paths are resolved from the project directory, so execution does not depend on the current working directory. Imports do not execute the pipeline.

All seven SQL analyses live in `sql/queries.sql`, separated by `-- name:` comments. Run an individual section with `--query <name>` or the whole worksheet with `--query all`. The same file can be opened in a SQLite editor to run selected statements directly.

## Outputs

Generated in `data/processed/`:

| File | Purpose |
| --- | --- |
| `sales_processed.csv` | Validated order-level fact table for Power BI |
| `monthly_performance.csv` | Monthly amounts, ratios, coverage flags, MoM and YoY growth |
| `category_performance.csv` | Category revenue and return metrics |
| `region_performance.csv` | Regional performance |
| `product_id_performance.csv` | Product-level performance |
| `customer_id_performance.csv` | Observed customer revenue and order value |
| `discount_performance.csv` | Descriptive comparison across discount levels |
| `validation_summary.json` | Row counts, duplicate removals and amount reconciliation |
| `sales.db` | Sales fact and reporting tables for SQL |

Generated outputs are excluded from Git and rebuilt locally with `python main.py prepare`. All generated data, including the SQLite database, lives in `data/processed/`; the raw source remains included for reproducibility.

## Key methodological decisions

| Metric | Definition |
| --- | --- |
| Gross revenue | Price * quantity, before discounts and returns |
| Discount amount | Gross revenue minus revenue before returns |
| Revenue before returns (`revenue`) | Price * quantity * (1 - discount), rounded per order |
| Returned revenue | Revenue before returns for orders flagged as returned |
| Net revenue | Revenue before returns minus returned revenue; assumes a full refund |
| Orders / customers | Distinct IDs across all recorded orders, including returns |
| Net AOV | Estimated net revenue / all recorded orders |
| Return rate | Returned orders / all recorded orders |
| Weighted discount rate | Total discount amount / total gross revenue |

Shipping is excluded. Returns are attributed to the original order month because return dates are unavailable. The original `revenue` field retains its historical meaning for compatibility.

Invalid required values or conflicting order IDs stop preparation instead of being silently dropped. `total_amount` is checked against calculated revenue within one cent; mismatches are reported in the validation audit. The included source has no such mismatches.

Monthly comparisons use calendar months. Partial boundary months, missing comparators and zero denominators produce blank growth values. Coverage is inferred from the earliest and latest observed dates; it does not prove the source contains every transaction. Customer counts are not additive across reporting groups.

## Limitations

- The dataset is synthetic; findings illustrate an analytical approach and do not describe a verified business or national market.
- USD is a presentation assumption; the source currency is unspecified and no conversion has been applied.
- Net revenue is a full-refund estimate, not an accounting measure of realized cash or profit.
- No return dates or refund amounts are available; partial refunds cannot be modeled.
- Product IDs may appear across different categories; product reports aggregate the recorded ID without assuming a stable product-category dimension.
- Discount comparisons are descriptive and do not estimate promotional effectiveness.
- Partial September periods must not be treated as complete months.
- The scope is commercial performance. Customer segmentation belongs to Project 02; automation belongs to Project 03.

## Power BI

The DAX measures, visual theme and dashboard preview are in `powerbi/`. The reporting model uses the order-level sales fact table; aggregate exports provide reconciliation totals.

The intended story has three parts: establish net performance, explain the gross-to-net revenue bridge, and prioritize return investigations by category. Regional, product and customer views provide supporting detail. The visual direction uses the same teal and coral palette as Project 02.

Only the original dashboard screenshot is available. No editable `.pbix` or `.pbip` is included, so the interactive V2 has not been built or validated in Power BI.

## Visuals

Original dashboard, showing **revenue before returns**, not the new estimated net revenue metric:

![Original sales performance dashboard](powerbi/dashboard_screenshot.png)

## Portfolio alignment

This revision aligns Project 01 with [Project 02: E-commerce Customer Segmentation](https://github.com/Giandorsa/ecommerce-customer-segmentation) in three areas:

- **Reproducible structure:** a single command line entry point, focused Python modules, a SQL worksheet and business-rule checks.
- **Commercial clarity:** explicit revenue, discount and return definitions, reconciled reporting tables and documented analytical limitations.
- **Consistent communication:** a shared README narrative and dashboard palette, while keeping this project's focus on sales performance rather than segmentation.
