# ETL Lab Report

Student ID: 67160219
Name: Thanawat Phirin

## 1. Data Quality Problems Found

- `customers.csv` has 2 duplicate customer IDs, inconsistent province names, one missing province, and one missing email.
- `orders.csv` has 3 duplicate order IDs, mixed date formats, inconsistent status casing, and invalid quantity, unit price, discount, and date values.
- `products.json` contains nested fields, a comma-formatted price, and one missing category.

## 2. Cleaning / Transformation Rules

- Keep the first row for each duplicated business key.
- Standardize province names to Chonburi, Bangkok, Rayong, or Chanthaburi; use `Unknown` when missing/unmapped.
- Fill missing email and product category with `Unknown`.
- Flatten product JSON, rename nested fields, remove commas from price, and convert it to numeric.
- Parse mixed order dates, normalize status to lowercase, and keep only `paid`/`completed` orders.
- Reject invalid quantity, unit price, discount percentage, date, and missing customer/product master records.
- Calculate gross amount, discount amount, and net sales amount.

## 3. Rejected Records

Count: 4

Main reasons: invalid quantity (1), invalid discount percentage (1), invalid date (1), and invalid unit price (1).

## 4. ETL Validation

- Valid transformed rows: 100
- Warehouse rows: 100
- Duplicate order_id: 0
- Source total sales: 192074.66
- Warehouse total sales: 192074.66
- Validation status: PASS

## 5. Idempotency Test

Number of `fact_sales` rows after run 1: 100

Number of `fact_sales` rows after run 2: 100

The row count does not increase because `fact_sales.order_id` is a primary key and the loader uses `INSERT OR IGNORE`.
