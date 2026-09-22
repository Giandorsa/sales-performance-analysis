"""Command line entry point for sales performance analysis."""
import argparse
from pathlib import Path
from src.workflows import load_sql_queries, prepare_data, run_sql_analysis

PROJECT_ROOT = Path(__file__).resolve().parent


def main() -> None:
    """Dispatch the requested preparation or SQL workflow."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("prepare", help="Build validated sales and reporting tables.")
    commands.add_parser("all", help="Prepare data and execute all SQL analyses.")
    sql = commands.add_parser("sql", help="Execute a saved SQL analysis.")
    queries = list(load_sql_queries(PROJECT_ROOT))
    sql.add_argument("--query", choices=["all", *queries], default="sales_overview")
    args = parser.parse_args()
    if args.command in {"prepare", "all"}:
        prepare_data(PROJECT_ROOT)
    if args.command == "all" or (args.command == "sql" and args.query == "all"):
        for query in queries:
            run_sql_analysis(PROJECT_ROOT, query)
    elif args.command == "sql":
        run_sql_analysis(PROJECT_ROOT, args.query)


if __name__ == "__main__":
    main()
