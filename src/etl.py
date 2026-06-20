"""ETL pipeline: CSV files -> transform -> SQLite star schema."""
import logging
import os
import sqlite3

import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

DB_PATH  = 'data/warehouse.db'
DATA_DIR = 'data'


def extract():
    log.info('Extracting CSVs...')
    customers    = pd.read_csv(f'{DATA_DIR}/customers.csv')
    products     = pd.read_csv(f'{DATA_DIR}/products.csv')
    transactions = pd.read_csv(f'{DATA_DIR}/transactions.csv')
    log.info(f'Loaded {len(customers):,} customers | {len(products):,} products | {len(transactions):,} transactions')
    return customers, products, transactions


def transform(customers, products, transactions):
    log.info('Transforming...')
    transactions['order_date']        = pd.to_datetime(transactions['order_date'])
    customers['acquisition_date']     = pd.to_datetime(customers['acquisition_date'])
    customers['acquisition_month']    = customers['acquisition_date'].dt.to_period('M').astype(str)

    transactions['order_year']        = transactions['order_date'].dt.year
    transactions['order_month']       = transactions['order_date'].dt.month
    transactions['order_quarter']     = transactions['order_date'].dt.quarter
    transactions['order_week']        = transactions['order_date'].dt.isocalendar().week.astype(int)
    transactions['order_day_of_week'] = transactions['order_date'].dt.dayofweek
    transactions['year_month']        = transactions['order_date'].dt.to_period('M').astype(str)
    transactions['profit_margin']     = (transactions['profit'] / transactions['revenue'] * 100).round(2)
    transactions['order_date']        = transactions['order_date'].dt.strftime('%Y-%m-%d')

    return customers.dropna(), products.dropna(), transactions.dropna()


def load(customers, products, transactions):
    log.info(f'Loading into {DB_PATH}...')
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    with open('sql/schema.sql') as f:
        conn.executescript(f.read())

    customers.to_sql('dim_customers',       conn, if_exists='replace', index=False)
    products.to_sql('dim_products',         conn, if_exists='replace', index=False)
    transactions.to_sql('fact_transactions',conn, if_exists='replace', index=False)

    dates = pd.DataFrame({'date': pd.date_range('2021-01-01', '2023-12-31')})
    dates['year']        = dates['date'].dt.year
    dates['month']       = dates['date'].dt.month
    dates['quarter']     = dates['date'].dt.quarter
    dates['week']        = dates['date'].dt.isocalendar().week.astype(int)
    dates['day_of_week'] = dates['date'].dt.dayofweek
    dates['date']        = dates['date'].dt.strftime('%Y-%m-%d')
    dates.to_sql('dim_dates', conn, if_exists='replace', index=False)

    conn.commit()
    conn.close()
    log.info('Load complete')


def run_pipeline():
    if not os.path.exists(f'{DATA_DIR}/transactions.csv'):
        log.info('Data not found — generating...')
        from generate_data import main as gen
        gen()
    customers, products, transactions = extract()
    customers, products, transactions = transform(customers, products, transactions)
    load(customers, products, transactions)
    log.info('ETL pipeline finished')


if __name__ == '__main__':
    run_pipeline()
