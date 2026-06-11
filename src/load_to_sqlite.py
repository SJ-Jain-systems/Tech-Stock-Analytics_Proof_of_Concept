"""Load the cleaned technology stock dataset into SQLite."""

from pathlib import Path
import sqlite3

import pandas as pd


CLEAN_INPUT_PATH = Path("data/processed/tech_stocks_clean.csv")
DATABASE_PATH = Path("data/processed/tech_stocks.db")
CREATE_TABLES_SQL_PATH = Path("sql/01_create_tables.sql")
TABLE_NAME = "tech_stocks"
EXPECTED_COLUMNS = [
    "date",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "symbol",
    "trading_year",
    "trading_month",
]


def load_clean_data(csv_path):
    """Read and validate the cleaned stock CSV for SQLite loading."""
    data = pd.read_csv(csv_path)
    missing_columns = [column for column in EXPECTED_COLUMNS if column not in data.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns in cleaned data: {missing_columns}")
    return data[EXPECTED_COLUMNS]


def load_to_sqlite(csv_path=CLEAN_INPUT_PATH, database_path=DATABASE_PATH, sql_path=CREATE_TABLES_SQL_PATH):
    """Create the SQLite database and load the cleaned stock records."""
    csv_file = Path(csv_path)
    database_file = Path(database_path)
    sql_file = Path(sql_path)

    data = load_clean_data(csv_file)
    create_tables_sql = sql_file.read_text(encoding="utf-8")

    database_file.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_file) as connection:
        connection.executescript(create_tables_sql)
        data.to_sql(TABLE_NAME, connection, if_exists="append", index=False)

        row_count = connection.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}").fetchone()[0]
        unique_symbols = connection.execute(
            f"SELECT COUNT(DISTINCT symbol) FROM {TABLE_NAME}"
        ).fetchone()[0]
        min_date, max_date = connection.execute(
            f"SELECT MIN(date), MAX(date) FROM {TABLE_NAME}"
        ).fetchone()

    print(f"Loaded {row_count} rows into {database_file}")
    print(f"Unique symbols: {unique_symbols}")
    print(f"Date range: {min_date} to {max_date}")

    return row_count, unique_symbols, min_date, max_date


def main():
    """Run the SQLite loading workflow from the command line."""
    project_root = Path(__file__).resolve().parents[1]
    csv_path = project_root / CLEAN_INPUT_PATH
    database_path = project_root / DATABASE_PATH
    sql_path = project_root / CREATE_TABLES_SQL_PATH
    load_to_sqlite(csv_path, database_path, sql_path)


if __name__ == "__main__":
    main()
