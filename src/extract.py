import json
import sqlite3
import pandas as pd
from .config import RAW_DIR, SOURCE_DB

def extract_data():
    """
    TODO 1
    Extract data from:
      - customers.csv
      - orders.csv
      - products.json
      - stores table in store.db
    Return a dictionary of DataFrames.
    """

    customers = pd.read_csv(RAW_DIR / "customers.csv")
    orders = pd.read_csv(RAW_DIR / "orders.csv")

    with open(RAW_DIR / "products.json", encoding="utf-8") as file:
        products = pd.json_normalize(json.load(file))

    with sqlite3.connect(SOURCE_DB) as connection:
        stores = pd.read_sql_query("SELECT * FROM stores", connection)

    return {
        "customers": customers,
        "orders": orders,
        "products": products,
        "stores": stores,
    }
