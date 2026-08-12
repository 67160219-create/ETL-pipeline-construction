import sqlite3
import pandas as pd
from .config import WAREHOUSE_DB

def load_data(customers, products, sales):
    """
    TODO 3

    Create/load these tables:
      dim_customer
      dim_product
      fact_sales

    Requirements:
    - customer_id unique in dim_customer
    - product_id unique in dim_product
    - order_id unique in fact_sales
    - running the pipeline twice must NOT duplicate fact_sales

    Hint:
    Use SQLite UNIQUE constraints and INSERT OR IGNORE / upsert logic.
    """
    WAREHOUSE_DB.parent.mkdir(parents=True, exist_ok=True)

    schema = """
    CREATE TABLE IF NOT EXISTS dim_customer (
        customer_id TEXT PRIMARY KEY,
        name TEXT,
        province TEXT,
        email TEXT
    );
    CREATE TABLE IF NOT EXISTS dim_product (
        product_id TEXT PRIMARY KEY,
        product_name TEXT,
        category TEXT,
        price REAL
    );
    CREATE TABLE IF NOT EXISTS fact_sales (
        order_id TEXT PRIMARY KEY,
        customer_id TEXT,
        product_id TEXT,
        order_date TEXT,
        qty INTEGER,
        unit_price REAL,
        discount_pct REAL,
        sales_amount REAL,
        FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
        FOREIGN KEY (product_id) REFERENCES dim_product(product_id)
    );
    """

    with sqlite3.connect(WAREHOUSE_DB) as connection:
        connection.executescript(schema)
        connection.executemany(
            "INSERT OR REPLACE INTO dim_customer VALUES (?, ?, ?, ?)",
            customers[["customer_id", "name", "province", "email"]]
            .itertuples(index=False, name=None),
        )
        connection.executemany(
            "INSERT OR REPLACE INTO dim_product VALUES (?, ?, ?, ?)",
            products[["product_id", "product_name", "category", "price"]]
            .itertuples(index=False, name=None),
        )

        fact = sales[
            [
                "order_id",
                "customer_id",
                "product_id",
                "order_date",
                "qty",
                "unit_price",
                "discount_pct",
                "sales_amount",
            ]
        ].copy()
        fact["order_date"] = pd.to_datetime(fact["order_date"]).dt.strftime("%Y-%m-%d")
        connection.executemany(
            "INSERT OR IGNORE INTO fact_sales VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            fact.itertuples(index=False, name=None),
        )
