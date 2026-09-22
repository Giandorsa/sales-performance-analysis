"""Business-rule and reconciliation checks using small, known orders."""
import sqlite3
from pathlib import Path

import pandas as pd
import pytest

from src.data_cleaning import clean_sales
from src.sales_reporting import build_reports
from src.workflows import load_sql_queries, replace_tables


def source():
    return pd.DataFrame([
        dict(order_id="O1", customer_id="C1", product_id="P1", category="Home",
             region="South", order_date="2024-01-01", price=100, quantity=2,
             discount=0.1, shipping_cost=10, total_amount=180, returned="No"),
        dict(order_id="O2", customer_id="C1", product_id="P2", category="Home",
             region="South", order_date="2024-01-31", price=50, quantity=1,
             discount=0, shipping_cost=5, total_amount=50, returned=" Yes "),
    ])


def test_revenue_bridge_and_duplicate_audit():
    raw = source()
    sales, audit = clean_sales(pd.concat([raw, raw.iloc[:1]]))
    assert audit["exact_duplicates_removed"] == 1
    assert sales.gross_revenue.sum() == 250
    assert sales.discount_amount.sum() == 20
    assert sales.revenue.sum() == 230
    assert sales.returned_revenue.sum() == 50
    assert sales.net_revenue.sum() == 180
    report = build_reports(sales)["category_performance"].iloc[0]
    assert report.customers == 1
    assert report.average_order_value == 90
    assert report.return_rate == 0.5


@pytest.mark.parametrize("field,value", [
    ("discount", 1.1), ("price", float("inf")), ("quantity", 1.5),
    ("returned", "unknown"), ("order_date", "invalid"), ("customer_id", " "),
])
def test_invalid_business_values_are_rejected(field, value):
    raw = source()
    raw[field] = raw[field].astype(object)
    raw.loc[0, field] = value
    with pytest.raises(ValueError):
        clean_sales(raw)


def test_conflicting_orders_are_rejected():
    raw = source()
    raw.loc[1, "order_id"] = "O1"
    with pytest.raises(ValueError, match="one row per order"):
        clean_sales(raw)


def test_missing_months_and_partial_months_do_not_create_growth():
    raw = pd.concat([source()] * 3, ignore_index=True)
    raw["order_id"] = [f"O{i}" for i in range(6)]
    raw["order_date"] = ["2024-01-12", "2024-01-31", "2024-02-01",
                         "2024-02-29", "2024-04-01", "2024-04-15"]
    monthly = build_reports(clean_sales(raw)[0])["monthly_performance"].set_index("month_year")
    assert list(monthly.index) == ["2024-01", "2024-02", "2024-03", "2024-04"]
    assert monthly.mom_growth.isna().all()
    assert monthly.yoy_growth.isna().all()


def test_complete_month_growth_and_zero_denominator():
    raw = pd.concat([source()] * 2, ignore_index=True)
    raw["order_id"] = [f"O{i}" for i in range(4)]
    raw["order_date"] = ["2024-01-01", "2024-01-31", "2024-02-01", "2024-02-29"]
    monthly = build_reports(clean_sales(raw)[0])["monthly_performance"]
    assert monthly.iloc[1].mom_growth == 0
    raw.loc[:1, "returned"] = "Yes"
    monthly = build_reports(clean_sales(raw)[0])["monthly_performance"]
    assert pd.isna(monthly.iloc[1].mom_growth)


def test_sql_reconciles_and_repeat_run_replaces_tables(tmp_path):
    sales, _ = clean_sales(source())
    tables = {"sales": sales, **build_reports(sales)}
    path = tmp_path / "sales.db"
    replace_tables(tables, path)
    replace_tables(tables, path)
    root = Path(__file__).resolve().parents[1]
    queries = load_sql_queries(root)
    assert set(queries) == {"sales_overview", "category_performance", "region_performance",
                            "monthly_performance", "top_products", "top_customers",
                            "discount_analysis"}
    with sqlite3.connect(path) as connection:
        for query in queries.values():
            result = pd.read_sql_query(query, connection)
            assert not result.empty
        result = pd.read_sql_query(queries["sales_overview"], connection).iloc[0]
    assert result.orders == 2
    assert result.net_revenue == 180
    assert result.average_order_value == 90


def test_yoy_uses_same_calendar_month():
    raw = pd.concat([source()] * 2, ignore_index=True)
    raw["order_id"] = [f"O{i}" for i in range(4)]
    raw["order_date"] = ["2024-01-01", "2024-01-31", "2025-01-01", "2025-01-31"]
    raw.loc[2:, "price"] *= 2
    monthly = build_reports(clean_sales(raw)[0])["monthly_performance"]
    assert monthly.iloc[-1].yoy_growth == 1
    assert pd.isna(monthly.iloc[-1].mom_growth)
