"""Workflows exposed through the shared portfolio command line pattern."""
import json
import re
import sqlite3
from contextlib import closing
from pathlib import Path
import pandas as pd
from src.data_cleaning import build_sales
from src.sales_reporting import build_reports


def replace_tables(tables: dict[str, pd.DataFrame], database_path: Path) -> None:
    """Save analytical tables to SQLite, replacing previous generated results."""
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(database_path)) as connection:
        for name, table in tables.items():
            table.to_sql(name, connection, if_exists="replace", index=False)


def prepare_data(project_root: Path) -> None:
    """Validate source orders and rebuild local CSV and SQLite outputs."""
    sales, audit = build_sales(project_root / "data/raw/dataset.csv")
    output = project_root / "data/processed"
    output.mkdir(parents=True, exist_ok=True)
    reports = build_reports(sales)
    for name, data in {"sales_processed": sales, **reports}.items():
        data.to_csv(output / f"{name}.csv", index=False)
    replace_tables({"sales": sales, **reports}, output / "sales.db")
    (output / "validation_summary.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print("Data preparation completed successfully.")
    print(json.dumps(audit, indent=2))
    print(f"Processed data: {output}")


def load_sql_queries(project_root: Path) -> dict[str, str]:
    """Read query sections marked with -- name: from the shared SQL worksheet."""
    worksheet = (project_root / "sql/queries.sql").read_text(encoding="utf-8")
    sections = re.split(r"^-- name: ([a-z][a-z0-9_]*)\s*$", worksheet, flags=re.MULTILINE)
    queries = {}
    for name, query in zip(sections[1::2], sections[2::2]):
        if name in queries or not query.strip():
            raise ValueError(f"Duplicate or empty SQL section: {name}")
        queries[name] = query.strip()
    if not queries:
        raise ValueError("No named queries found in sql/queries.sql.")
    return queries


def run_sql_analysis(project_root: Path, query_name: str) -> pd.DataFrame:
    """Execute one worksheet section against the existing read-only database."""
    database = project_root / "data/processed/sales.db"
    queries = load_sql_queries(project_root)
    if query_name not in queries:
        raise ValueError(f"Unknown query: {query_name}")
    if not database.exists():
        raise FileNotFoundError("Run `python main.py prepare` before SQL queries.")
    with closing(sqlite3.connect(database.as_uri() + "?mode=ro", uri=True)) as connection:
        result = pd.read_sql_query(queries[query_name], connection)
    print(f"\n{query_name}: {len(result):,} rows")
    print(result.to_string(index=False))
    return result
