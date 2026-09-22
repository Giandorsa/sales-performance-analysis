"""Validate order-level sales and make revenue definitions explicit."""
from pathlib import Path
import numpy as np
import pandas as pd

REQUIRED = ["order_id", "customer_id", "product_id", "category", "region",
            "order_date", "price", "quantity", "discount", "shipping_cost",
            "total_amount", "returned"]


def build_sales(raw_path: Path) -> tuple[pd.DataFrame, dict]:
    """Read CSV and return validated sales plus a preparation audit."""
    return clean_sales(pd.read_csv(raw_path, dtype={c: "string" for c in
                      ["order_id", "customer_id", "product_id"]}))


def clean_sales(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Remove exact duplicates and reject invalid business fields explicitly."""
    missing = sorted(set(REQUIRED) - set(raw.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    sales = raw.drop_duplicates().copy()
    for column in ["order_id", "customer_id", "product_id", "category", "region", "returned"]:
        sales[column] = sales[column].astype("string").str.strip().replace("", pd.NA)
    if sales.empty or sales[REQUIRED].isna().any().any():
        raise ValueError("Source is empty or contains missing required values.")
    if sales.order_id.duplicated().any():
        raise ValueError("Expected one row per order; conflicting order IDs found.")
    sales["order_date"] = pd.to_datetime(
        sales.order_date, format="%Y-%m-%d", errors="raise"
    ).dt.normalize()
    if sales.order_date.isna().any():
        raise ValueError("Missing order date.")
    numeric = ["price", "quantity", "discount", "shipping_cost", "total_amount"]
    sales[numeric] = sales[numeric].apply(pd.to_numeric, errors="raise")
    valid = (np.isfinite(sales[numeric]).all(axis=1)
             & sales.price.gt(0) & sales.quantity.gt(0)
             & sales.quantity.mod(1).eq(0) & sales.discount.between(0, 1)
             & sales.shipping_cost.ge(0) & sales.total_amount.ge(0))
    returned = sales.returned.str.lower()
    if not valid.all() or not returned.isin(["yes", "no"]).all():
        raise ValueError("Invalid price, quantity, discount, shipping, amount or return flag.")
    sales["is_returned"] = returned.eq("yes").astype(int)
    sales["gross_revenue"] = (sales.price * sales.quantity).round(2)
    sales["revenue"] = (sales.price * sales.quantity * (1 - sales.discount)).round(2)
    sales["discount_amount"] = (sales.gross_revenue - sales.revenue).round(2)
    sales["returned_revenue"] = sales.revenue * sales.is_returned
    sales["net_revenue"] = (sales.revenue - sales.returned_revenue).round(2)
    sales["month_year"] = sales.order_date.dt.to_period("M").astype(str)
    audit = {"source_rows": len(raw), "exact_duplicates_removed": len(raw) - len(sales),
             "orders": len(sales), "customers": sales.customer_id.nunique(),
             "amount_mismatches_over_one_cent": int(((sales.revenue - sales.total_amount).abs() > 0.010001).sum())}
    return sales, audit
