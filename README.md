# End-to-End Business Intelligence Pipeline

A production-grade BI pipeline built with Python, SQL, and Plotly Dash — demonstrating the full lifecycle from raw data generation through ETL, star-schema warehousing, analytical SQL queries, and an interactive executive dashboard.

## Architecture

```
Data Generation  →  ETL Pipeline  →  SQLite Star Schema  →  SQL Analytics  →  Plotly Dash Dashboard
  (50K+ rows)       (extract /          (4 tables)          (revenue /         (5 KPI panels,
                    transform /                              cohort /            real-time filters)
                    load)                                    CLV queries)
```

## Tech Stack

| Layer        | Tool                        |
|--------------|-----------------------------|
| Language     | Python 3.10+                |
| Data         | Pandas, NumPy               |
| Warehouse    | SQLite (star schema)        |
| SQL Analysis | Analytical SQL (CTEs, Window functions) |
| Dashboard    | Plotly Dash                 |
| BI Tool      | Power BI (export-compatible)|

## Project Structure

```
business-intelligence-pipeline/
├── src/
│   ├── generate_data.py   # Synthetic 50K+ transaction generator
│   ├── etl.py             # Extract → Transform → Load pipeline
│   └── dashboard.py       # Plotly Dash interactive dashboard
├── sql/
│   ├── schema.sql         # Star schema DDL (4 tables)
│   └── queries/
│       ├── revenue_analysis.sql   # 6 revenue KPI queries
│       ├── cohort_analysis.sql    # Cohort retention + repeat rate
│       └── clv_estimation.sql     # Customer Lifetime Value
├── data/                  # Generated at runtime (gitignored)
├── requirements.txt
└── Makefile
```

## Dataset

Synthetically generated with `numpy.random` (seed=42 for reproducibility):

| Table              | Rows     | Description                        |
|--------------------|----------|------------------------------------|
| `dim_customers`    | 5,000    | Region, segment, acquisition date  |
| `dim_products`     | 500      | 5 categories, pricing, cost        |
| `fact_transactions`| 50,000   | Orders with revenue, profit, dates |
| `dim_dates`        | 1,096    | Calendar dimension (2021–2023)     |

## SQL Analytics

### Revenue Analysis
- Monthly revenue trend with AOV and profit margin
- Revenue by product category and subcategory
- Revenue by region × segment cross-tab
- Top 10 products by revenue
- QoQ growth rate (window function `LAG`)
- Discount band impact on margin

### Cohort Analysis
- Monthly retention matrix (cohort × activity month)
- Repeat purchase rate by month
- Average inter-order interval per customer

### CLV Estimation
- Annualised revenue rate per customer
- Value tier segmentation (High / Medium / Low)
- CLV summary by customer segment

## Dashboard

Interactive Plotly Dash app with year and region filters:

- **KPI Cards** — Revenue, Profit, Orders, Customers, AOV
- **Monthly Revenue Trend** — bar + line overlay
- **Category Revenue** — pie chart breakdown
- **Region Performance** — horizontal bar chart
- **Segment Comparison** — Revenue vs Profit grouped bars
- **Cohort Retention Heatmap** — 12×12 retention matrix

## Quick Start

```bash
pip install -r requirements.txt
make all          # generate data + run ETL
make dashboard    # open http://localhost:8050
```

## Key Design Decisions

- **SQLite** — zero-infrastructure; schema mirrors PostgreSQL for easy migration
- **Seed=42** — reproducible data generation
- **Star schema** — fact + 3 dimension tables mirrors production DWH patterns
- **Idempotent ETL** — safe re-runs without data duplication
- **Power BI compatible** — SQLite connects via ODBC for production dashboards
