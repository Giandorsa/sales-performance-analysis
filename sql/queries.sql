-- Overall sales performance metrics

SELECT
    ROUND(SUM(revenue), 2) AS total_revenue,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS total_customers,
    ROUND(
        SUM(revenue) / COUNT(DISTINCT order_id),
        2
    ) AS average_order_value
FROM sales;


-- Revenue by category

SELECT
    category,
    ROUND(SUM(revenue), 2) AS total_revenue
FROM sales
GROUP BY category
ORDER BY total_revenue DESC;


-- Revenue by region

SELECT
    region,
    ROUND(SUM(revenue), 2) AS total_revenue
FROM sales
GROUP BY region
ORDER BY total_revenue DESC;


-- Monthly revenue

SELECT
    month_year,
    ROUND(SUM(revenue), 2) AS total_revenue
FROM sales
GROUP BY month_year
ORDER BY month_year;


-- Top products

SELECT
    product_id,
    category,
    ROUND(SUM(revenue), 2) AS total_revenue
FROM sales
GROUP BY product_id, category
ORDER BY total_revenue DESC
LIMIT 10;


-- Top customers

SELECT
    customer_id,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(
        SUM(revenue) / COUNT(DISTINCT order_id),
        2
    ) AS average_order_value
FROM sales
GROUP BY customer_id
ORDER BY total_revenue DESC
LIMIT 10;