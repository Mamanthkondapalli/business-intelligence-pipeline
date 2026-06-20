"""Generate 50,000+ synthetic retail transactions for the BI pipeline."""
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

RNG        = np.random.default_rng(42)
N_CUST     = 5_000
N_PROD     = 500
N_ORDERS   = 50_000
START_DATE = datetime(2021, 1, 1)
END_DATE   = datetime(2023, 12, 31)
DATA_DIR   = 'data'


def generate_customers() -> pd.DataFrame:
    regions  = ['North', 'South', 'East', 'West', 'Central']
    segments = ['Consumer', 'Corporate', 'Home Office']
    n = N_CUST
    offsets = RNG.integers(0, 365, n)
    return pd.DataFrame({
        'customer_id':    [f'CUST{i:05d}' for i in range(1, n + 1)],
        'customer_name':  [f'Customer_{i}' for i in range(1, n + 1)],
        'region':         RNG.choice(regions, n),
        'segment':        RNG.choice(segments, n, p=[0.5, 0.3, 0.2]),
        'acquisition_date': [
            (START_DATE + timedelta(days=int(d))).strftime('%Y-%m-%d')
            for d in offsets
        ],
    })


def generate_products() -> pd.DataFrame:
    catalog = {
        'Electronics':     ['Phones', 'Laptops', 'Tablets', 'Accessories'],
        'Furniture':       ['Chairs', 'Tables', 'Storage', 'Bookcases'],
        'Office Supplies': ['Paper', 'Binders', 'Pens', 'Labels'],
        'Clothing':        ['Shirts', 'Pants', 'Shoes', 'Accessories'],
        'Food & Beverage': ['Snacks', 'Beverages', 'Meals', 'Condiments'],
    }
    rows = []
    for i in range(1, N_PROD + 1):
        cat   = RNG.choice(list(catalog))
        sub   = RNG.choice(catalog[cat])
        price = round(float(RNG.uniform(5, 2000)), 2)
        cost  = round(price * float(RNG.uniform(0.4, 0.7)), 2)
        rows.append({
            'product_id':   f'PROD{i:04d}',
            'product_name': f'{sub}_Product_{i}',
            'category':     cat,
            'subcategory':  sub,
            'unit_price':   price,
            'unit_cost':    cost,
        })
    return pd.DataFrame(rows)


def generate_transactions(customers: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    n           = N_ORDERS
    total_days  = (END_DATE - START_DATE).days
    cust_idx    = RNG.integers(0, len(customers), n)
    prod_idx    = RNG.integers(0, len(products),  n)
    day_offsets = RNG.integers(0, total_days, n)
    quantities  = RNG.integers(1, 10, n)
    discounts   = RNG.choice([0.0, 0.05, 0.10, 0.15, 0.20], n, p=[0.50, 0.15, 0.15, 0.10, 0.10])

    c = customers.iloc[cust_idx].reset_index(drop=True)
    p = products.iloc[prod_idx].reset_index(drop=True)

    revenues = (quantities * p['unit_price'].values * (1 - discounts)).round(2)
    costs    = (quantities * p['unit_cost'].values).round(2)

    return pd.DataFrame({
        'order_id':    [f'ORD{i:06d}' for i in range(1, n + 1)],
        'order_date':  [(START_DATE + timedelta(days=int(d))).strftime('%Y-%m-%d') for d in day_offsets],
        'customer_id': c['customer_id'].values,
        'product_id':  p['product_id'].values,
        'quantity':    quantities,
        'unit_price':  p['unit_price'].values,
        'discount':    discounts,
        'revenue':     revenues,
        'cost':        costs,
        'profit':      (revenues - costs).round(2),
        'region':      c['region'].values,
        'segment':     c['segment'].values,
    })


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    print('Generating customers...')
    customers = generate_customers()
    print('Generating products...')
    products  = generate_products()
    print('Generating transactions...')
    txns      = generate_transactions(customers, products)

    customers.to_csv(f'{DATA_DIR}/customers.csv',    index=False)
    products.to_csv(f'{DATA_DIR}/products.csv',      index=False)
    txns.to_csv(f'{DATA_DIR}/transactions.csv',      index=False)

    print(f'Done: {len(customers):,} customers | {len(products):,} products | {len(txns):,} transactions')


if __name__ == '__main__':
    main()
