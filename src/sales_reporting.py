"""Reconciliation tables for SQL analysis and Power BI."""
import pandas as pd


def summarize(sales: pd.DataFrame, dimension: str) -> pd.DataFrame:
    """Aggregate amounts and recalculate ratios at the requested grain."""
    result = sales.groupby(dimension, as_index=False).agg(
        orders=("order_id", "nunique"), customers=("customer_id", "nunique"),
        gross_revenue=("gross_revenue", "sum"), discount_amount=("discount_amount", "sum"),
        revenue=("revenue", "sum"), returned_revenue=("returned_revenue", "sum"),
        net_revenue=("net_revenue", "sum"), returned_orders=("is_returned", "sum"))
    result["return_rate"] = result.returned_orders / result.orders
    result["average_order_value"] = result.net_revenue / result.orders
    result["weighted_discount_rate"] = result.discount_amount / result.gross_revenue
    return result


def build_reports(sales: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Compare calendar months only when both periods have complete coverage."""
    monthly = summarize(sales, "month_year").set_index("month_year")
    periods = pd.period_range(sales.order_date.min(), sales.order_date.max(), freq="M")
    monthly = monthly.reindex(periods.astype(str)).rename_axis("month_year")
    monthly["is_complete_month"] = [
        p.start_time >= sales.order_date.min() and p.end_time.normalize() <= sales.order_date.max()
        for p in periods]
    for label, lag in [("mom", 1), ("yoy", 12)]:
        previous = monthly.net_revenue.shift(lag)
        comparable = monthly.is_complete_month & monthly.is_complete_month.shift(lag, fill_value=False)
        monthly[f"{label}_growth"] = (monthly.net_revenue / previous.where(previous.ne(0)) - 1).where(comparable)
    return {"monthly_performance": monthly.reset_index(),
            **{f"{dimension}_performance": summarize(sales, dimension)
               for dimension in ["category", "region", "product_id", "customer_id", "discount"]}}
