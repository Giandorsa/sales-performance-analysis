-- Sales performance analyses. Run against data/processed/sales.db.
-- Each -- name: marker identifies a query for the command line interface.

-- name: sales_overview
-- Full-refund assumption; shipping excluded. Ratios use all recorded orders.
SELECT COUNT(*) AS orders, COUNT(DISTINCT customer_id) AS customers,
       ROUND(SUM(gross_revenue), 2) AS gross_revenue,
       ROUND(SUM(discount_amount), 2) AS discount_amount,
       ROUND(SUM(revenue), 2) AS revenue_before_returns,
       ROUND(SUM(returned_revenue), 2) AS returned_revenue,
       ROUND(SUM(net_revenue), 2) AS net_revenue,
       ROUND(SUM(net_revenue) / COUNT(*), 2) AS average_order_value,
       ROUND(1.0 * SUM(is_returned) / COUNT(*), 6) AS return_rate
FROM sales;

-- name: category_performance
SELECT * FROM category_performance ORDER BY net_revenue DESC;

-- name: region_performance
SELECT * FROM region_performance ORDER BY net_revenue DESC;

-- name: monthly_performance
-- Growth excludes partial months and missing or zero comparators.
SELECT * FROM monthly_performance ORDER BY month_year;

-- name: top_products
SELECT * FROM product_id_performance ORDER BY net_revenue DESC, product_id LIMIT 10;

-- name: top_customers
SELECT * FROM customer_id_performance ORDER BY net_revenue DESC, customer_id LIMIT 10;

-- name: discount_analysis
-- Observational comparison; discounts are not randomly assigned.
SELECT * FROM discount_performance ORDER BY discount;
