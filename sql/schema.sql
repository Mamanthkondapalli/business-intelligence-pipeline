-- Star schema for retail analytics warehouse

DROP TABLE IF EXISTS fact_transactions;
DROP TABLE IF EXISTS dim_customers;
DROP TABLE IF EXISTS dim_products;
DROP TABLE IF EXISTS dim_dates;

CREATE TABLE IF NOT EXISTS dim_customers (
    customer_id       TEXT PRIMARY KEY,
    customer_name     TEXT,
    region            TEXT,
    segment           TEXT,
    acquisition_date  TEXT,
    acquisition_month TEXT
);

CREATE TABLE IF NOT EXISTS dim_products (
    product_id   TEXT PRIMARY KEY,
    product_name TEXT,
    category     TEXT,
    subcategory  TEXT,
    unit_price   REAL,
    unit_cost    REAL
);

CREATE TABLE IF NOT EXISTS dim_dates (
    date        TEXT PRIMARY KEY,
    year        INTEGER,
    month       INTEGER,
    quarter     INTEGER,
    week        INTEGER,
    day_of_week INTEGER
);

CREATE TABLE IF NOT EXISTS fact_transactions (
    order_id          TEXT PRIMARY KEY,
    order_date        TEXT,
    customer_id       TEXT,
    product_id        TEXT,
    quantity          INTEGER,
    unit_price        REAL,
    discount          REAL,
    revenue           REAL,
    cost              REAL,
    profit            REAL,
    region            TEXT,
    segment           TEXT,
    order_year        INTEGER,
    order_month       INTEGER,
    order_quarter     INTEGER,
    order_week        INTEGER,
    order_day_of_week INTEGER,
    year_month        TEXT,
    profit_margin     REAL,
    FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id),
    FOREIGN KEY (product_id)  REFERENCES dim_products(product_id)
);
