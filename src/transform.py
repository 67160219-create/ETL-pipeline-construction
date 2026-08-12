import pandas as pd
from .config import PROVINCE_MAP

def transform_data(raw):
    """
    TODO 2

    Customers:
    - remove duplicate customer_id
    - standardize province
    - handle missing province/email

    Products:
    - flatten nested JSON fields
    - rename fields
    - convert price to numeric
    - fill missing category with "Unknown"

    Orders:
    - remove duplicate order_id
    - parse mixed date formats
    - normalize status
    - reject invalid records:
        qty <= 0
        unit_price <= 0
        discount_pct < 0 or > 100
        invalid order_date

    Merge:
    - keep paid/completed orders
    - join customers + products
    - reject unknown customer/product

    Calculate:
        gross_amount = qty * unit_price
        discount_amount = gross_amount * discount_pct / 100
        sales_amount = gross_amount - discount_amount

    Return:
        clean_customers,
        clean_products,
        sales,
        rejects
    """
    customers = raw["customers"].copy()
    products = raw["products"].copy()
    orders = raw["orders"].copy()

    # Customers
    customers = customers.drop_duplicates("customer_id", keep="first")
    customers["province"] = (
        customers["province"]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
        .str.lower()
        .map(PROVINCE_MAP)
        .fillna("Unknown")
    )
    customers["email"] = customers["email"].fillna("Unknown")

    # Products (the nested fields were flattened by pd.json_normalize).
    products = products.rename(
        columns={"category.name": "category", "pricing.price": "price"}
    ).drop_duplicates("product_id", keep="first")
    products["category"] = products["category"].fillna("Unknown")
    products["price"] = pd.to_numeric(
        products["price"].astype(str).str.replace(",", "", regex=False),
        errors="coerce",
    )

    # Orders
    orders = orders.drop_duplicates("order_id", keep="first")
    for column in ["qty", "unit_price", "discount_pct"]:
        orders[column] = pd.to_numeric(orders[column], errors="coerce")
    orders["order_date"] = pd.to_datetime(
        orders["order_date"], format="mixed", dayfirst=True, errors="coerce"
    )
    orders["status"] = orders["status"].astype(str).str.strip().str.lower()

    invalid_rules = {
        "invalid_qty": orders["qty"].isna() | (orders["qty"] <= 0),
        "invalid_unit_price": orders["unit_price"].isna()
        | (orders["unit_price"] <= 0),
        "invalid_discount_pct": orders["discount_pct"].isna()
        | ~orders["discount_pct"].between(0, 100),
        "invalid_order_date": orders["order_date"].isna(),
    }
    invalid_mask = pd.Series(False, index=orders.index)
    for mask in invalid_rules.values():
        invalid_mask |= mask

    invalid_rejects = orders.loc[invalid_mask].copy()
    invalid_rejects["reject_reason"] = [
        ", ".join(reason for reason, mask in invalid_rules.items() if mask.loc[index])
        for index in invalid_rejects.index
    ]

    valid_orders = orders.loc[~invalid_mask]
    valid_orders = valid_orders[valid_orders["status"].isin(["paid", "completed"])]

    merged = valid_orders.merge(
        customers, on="customer_id", how="left", indicator="customer_match"
    )
    merged = merged.merge(
        products, on="product_id", how="left", indicator="product_match"
    )

    unknown_mask = (merged["customer_match"] != "both") | (
        merged["product_match"] != "both"
    )
    unknown_rejects = merged.loc[unknown_mask, orders.columns].copy()
    unknown_rejects["reject_reason"] = ""
    unknown_rejects.loc[
        merged.loc[unknown_mask, "customer_match"] != "both", "reject_reason"
    ] = "unknown_customer"
    unknown_product = merged.loc[unknown_mask, "product_match"] != "both"
    unknown_rejects.loc[unknown_product, "reject_reason"] = (
        unknown_rejects.loc[unknown_product, "reject_reason"]
        .replace("", "unknown_product")
        .replace("unknown_customer", "unknown_customer, unknown_product")
    )

    sales = merged.loc[~unknown_mask].copy()
    sales["gross_amount"] = sales["qty"] * sales["unit_price"]
    sales["discount_amount"] = (
        sales["gross_amount"] * sales["discount_pct"] / 100
    )
    sales["sales_amount"] = sales["gross_amount"] - sales["discount_amount"]

    rejects = pd.concat([invalid_rejects, unknown_rejects], ignore_index=True)
    rejects["order_date"] = rejects["order_date"].astype("string")
    return customers, products, sales, rejects
