-- ============================================================
-- Customer Lifetime Value (CLV) Estimation
-- ============================================================

-- 1. Individual CLV with value-tier segmentation
WITH customer_metrics AS (
    SELECT
        customer_id,
        MIN(order_date)             AS first_order,
        MAX(order_date)             AS last_order,
        COUNT(DISTINCT order_id)    AS total_orders,
        ROUND(SUM(revenue), 2)      AS total_revenue,
        ROUND(AVG(revenue), 2)      AS avg_order_value,
        ROUND(SUM(profit), 2)       AS total_profit,
        JULIANDAY(MAX(order_date)) - JULIANDAY(MIN(order_date)) AS lifetime_days
    FROM fact_transactions
    GROUP BY customer_id
),
clv AS (
    SELECT
        cm.*,
        c.region,
        c.segment,
        CASE
            WHEN lifetime_days = 0 THEN total_revenue
            ELSE ROUND(total_revenue / (lifetime_days / 365.0), 2)
        END AS annualised_revenue,
        CASE
            WHEN total_revenue > 5000 THEN 'High Value'
            WHEN total_revenue > 1000 THEN 'Medium Value'
            ELSE 'Low Value'
        END AS value_tier
    FROM customer_metrics cm
    JOIN dim_customers c ON cm.customer_id = c.customer_id
)
SELECT * FROM clv ORDER BY total_revenue DESC;

-- 2. CLV summary by customer segment
SELECT
    segment,
    COUNT(*)                      AS customers,
    ROUND(AVG(total_revenue), 2)  AS avg_clv,
    ROUND(MAX(total_revenue), 2)  AS max_clv,
    ROUND(SUM(total_revenue), 2)  AS segment_total_revenue
FROM (
    SELECT customer_id, segment, SUM(revenue) AS total_revenue
    FROM fact_transactions
    JOIN dim_customers USING (customer_id)
    GROUP BY customer_id, segment
)
GROUP BY segment
ORDER BY avg_clv DESC;

-- 3. High-value customer geographic profile
SELECT
    c.region,
    c.segment,
    COUNT(DISTINCT t.customer_id)    AS high_value_customers,
    ROUND(AVG(t.revenue), 2)         AS avg_order_value,
    ROUND(AVG(clv.total_revenue), 2) AS avg_clv
FROM fact_transactions t
JOIN dim_customers c ON t.customer_id = c.customer_id
JOIN (
    SELECT customer_id, SUM(revenue) AS total_revenue
    FROM fact_transactions
    GROUP BY customer_id
    HAVING SUM(revenue) > 5000
) clv ON t.customer_id = clv.customer_id
GROUP BY c.region, c.segment
ORDER BY avg_clv DESC;
