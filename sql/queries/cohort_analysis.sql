-- ============================================================
-- Cohort Retention Analysis
-- ============================================================

-- 1. Monthly cohort retention matrix
WITH first_purchase AS (
    SELECT customer_id, MIN(year_month) AS cohort_month
    FROM fact_transactions
    GROUP BY customer_id
),
customer_activity AS (
    SELECT t.customer_id,
           t.year_month  AS activity_month,
           f.cohort_month
    FROM fact_transactions t
    JOIN first_purchase f ON t.customer_id = f.customer_id
),
cohort_counts AS (
    SELECT cohort_month, activity_month,
           COUNT(DISTINCT customer_id) AS active_customers
    FROM customer_activity
    GROUP BY cohort_month, activity_month
),
cohort_sizes AS (
    SELECT cohort_month, COUNT(DISTINCT customer_id) AS cohort_size
    FROM first_purchase
    GROUP BY cohort_month
)
SELECT
    cd.cohort_month,
    cd.activity_month,
    cs.cohort_size,
    cd.active_customers,
    ROUND(cd.active_customers * 100.0 / cs.cohort_size, 2) AS retention_rate_pct
FROM cohort_counts cd
JOIN cohort_sizes cs ON cd.cohort_month = cs.cohort_month
ORDER BY cd.cohort_month, cd.activity_month;

-- 2. Monthly repeat-purchase rate
SELECT
    year_month,
    COUNT(DISTINCT customer_id) AS total_customers,
    SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) AS repeat_customers,
    ROUND(
        SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) * 100.0
        / COUNT(DISTINCT customer_id), 2
    ) AS repeat_rate_pct
FROM (
    SELECT customer_id, year_month, COUNT(*) AS order_count
    FROM fact_transactions
    GROUP BY customer_id, year_month
)
GROUP BY year_month
ORDER BY year_month;

-- 3. Average days between orders
WITH ranked AS (
    SELECT customer_id, order_date,
           LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) AS prev_date
    FROM fact_transactions
)
SELECT
    customer_id,
    ROUND(AVG(JULIANDAY(order_date) - JULIANDAY(prev_date)), 1) AS avg_days_between_orders
FROM ranked
WHERE prev_date IS NOT NULL
GROUP BY customer_id
HAVING COUNT(*) >= 2
ORDER BY avg_days_between_orders;
