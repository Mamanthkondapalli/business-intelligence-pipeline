-- ============================================================
-- Revenue Analysis Queries
-- ============================================================

-- 1. Monthly revenue trend
SELECT
    year_month,
    COUNT(DISTINCT order_id)    AS total_orders,
    COUNT(DISTINCT customer_id) AS unique_customers,
    ROUND(SUM(revenue), 2)      AS total_revenue,
    ROUND(SUM(profit), 2)       AS total_profit,
    ROUND(AVG(profit_margin), 2) AS avg_profit_margin,
    ROUND(SUM(revenue) / COUNT(DISTINCT order_id), 2) AS avg_order_value
FROM fact_transactions
GROUP BY year_month
ORDER BY year_month;

-- 2. Revenue by product category
SELECT
    p.category,
    COUNT(DISTINCT t.order_id)     AS orders,
    ROUND(SUM(t.revenue), 2)       AS total_revenue,
    ROUND(SUM(t.profit), 2)        AS total_profit,
    ROUND(AVG(t.profit_margin), 2) AS avg_margin_pct
FROM fact_transactions t
JOIN dim_products p ON t.product_id = p.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;

-- 3. Revenue by region x segment
SELECT
    region,
    segment,
    ROUND(SUM(revenue), 2)      AS total_revenue,
    ROUND(SUM(profit), 2)       AS total_profit,
    COUNT(DISTINCT customer_id) AS customers,
    ROUND(SUM(revenue) / COUNT(DISTINCT customer_id), 2) AS revenue_per_customer
FROM fact_transactions
GROUP BY region, segment
ORDER BY total_revenue DESC;

-- 4. Top 10 products by revenue
SELECT
    p.product_name,
    p.category,
    COUNT(t.order_id)              AS orders,
    SUM(t.quantity)                AS units_sold,
    ROUND(SUM(t.revenue), 2)       AS total_revenue,
    ROUND(AVG(t.profit_margin), 2) AS avg_margin_pct
FROM fact_transactions t
JOIN dim_products p ON t.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_revenue DESC
LIMIT 10;

-- 5. Quarter-over-quarter revenue growth
WITH quarterly AS (
    SELECT order_year, order_quarter,
           ROUND(SUM(revenue), 2) AS revenue
    FROM fact_transactions
    GROUP BY order_year, order_quarter
),
with_prev AS (
    SELECT *,
        LAG(revenue) OVER (ORDER BY order_year, order_quarter) AS prev_revenue
    FROM quarterly
)
SELECT
    order_year, order_quarter, revenue,
    ROUND((revenue - prev_revenue) / prev_revenue * 100, 2) AS qoq_growth_pct
FROM with_prev
ORDER BY order_year, order_quarter;

-- 6. Discount impact on revenue and margin
SELECT
    CASE
        WHEN discount = 0    THEN 'No Discount'
        WHEN discount <= 0.1 THEN '1-10%'
        WHEN discount <= 0.2 THEN '11-20%'
        ELSE '20%+'
    END AS discount_band,
    COUNT(*)                     AS orders,
    ROUND(AVG(revenue), 2)       AS avg_order_revenue,
    ROUND(AVG(profit_margin), 2) AS avg_margin_pct
FROM fact_transactions
GROUP BY discount_band
ORDER BY avg_margin_pct DESC;
