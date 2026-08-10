import sqlite3
import pandas as pd

# Database

conn = sqlite3.connect("database/sales.db")


# Queries

with open("sql/queries.sql", "r", encoding="utf-8") as file:
    sql = file.read()


# Execute queries

queries = [
    query.strip()
    for query in sql.split(";")
    if query.strip()
]

for query in queries:
    result = pd.read_sql_query(query, conn)
    print("\n", result.to_string(index=False))


# Close connection

conn.close()