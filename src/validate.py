import sqlite3
from .config import WAREHOUSE_DB

def validate_data(source_sales):
    """
    TODO 4

    Return a dictionary with:
    - source_valid_rows
    - warehouse_rows
    - duplicate_order_ids
    - warehouse_total_sales
    - source_total_sales
    - status: PASS / FAIL
    """
    with sqlite3.connect(WAREHOUSE_DB) as connection:
        warehouse_rows = connection.execute(
            "SELECT COUNT(*) FROM fact_sales"
        ).fetchone()[0]
        duplicate_order_ids = connection.execute(
            """
            SELECT COUNT(*) FROM (
                SELECT order_id FROM fact_sales
                GROUP BY order_id HAVING COUNT(*) > 1
            )
            """
        ).fetchone()[0]
        warehouse_total_sales = connection.execute(
            "SELECT COALESCE(SUM(sales_amount), 0) FROM fact_sales"
        ).fetchone()[0]

    source_valid_rows = len(source_sales)
    source_total_sales = float(source_sales["sales_amount"].sum())
    passed = (
        source_valid_rows == warehouse_rows
        and duplicate_order_ids == 0
        and abs(source_total_sales - warehouse_total_sales) < 0.01
    )
    return {
        "source_valid_rows": source_valid_rows,
        "warehouse_rows": warehouse_rows,
        "duplicate_order_ids": duplicate_order_ids,
        "warehouse_total_sales": round(warehouse_total_sales, 2),
        "source_total_sales": round(source_total_sales, 2),
        "status": "PASS" if passed else "FAIL",
    }
