import os
import pandas as pd
import sqlite3

# Project setup

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

RAW_PATH = os.path.join(PROJECT_DIR, "data", "raw", "dataset.csv")

PROCESSED_DIR = os.path.join(PROJECT_DIR, "data", "processed")
PROCESSED_PATH = os.path.join(PROCESSED_DIR, "sales_processed.csv")

DATABASE_DIR = os.path.join(PROJECT_DIR, "database")
DATABASE_PATH = os.path.join(DATABASE_DIR, "sales.db")

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(DATABASE_DIR, exist_ok=True)


# Data loading

df = pd.read_csv(RAW_PATH)

print("Dataset loaded successfully")
print(f"Shape: {df.shape}")


# Data cleaning

df = df.drop_duplicates()

df["order_date"] = pd.to_datetime(df["order_date"])

df = df.dropna()

df = df[
    (df["price"] > 0) &
    (df["quantity"] > 0) &
    (df["total_amount"] > 0) &
    (df["shipping_cost"] >= 0)
].copy()


# Data transformation

df["revenue"] = (
    df["price"] * df["quantity"] * (1 - df["discount"])
).round(2)

df["month_year"] = (
    df["order_date"]
    .dt.to_period("M")
    .astype(str)
)

df["is_returned"] = (
    df["returned"]
    .str.lower() == "yes"
).astype(int)


# Save processed data

df.to_csv(PROCESSED_PATH, index=False)

print("Processed dataset saved successfully")
print(f"Shape: {df.shape}")


# Create SQLite database

conn = sqlite3.connect(DATABASE_PATH)

df.to_sql(
    "sales",
    conn,
    if_exists="replace",
    index=False
)

conn.close()

print("Database created successfully")
print(f"Database saved at: {DATABASE_PATH}")