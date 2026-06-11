"""Load the cleaned technology stock dataset into SQLite."""

from pathlib import Path
import sqlite3

import pandas as pd


CLEAN_INPUT_PATH = Path("data/processed/tech_stocks_clean.csv")
DATABASE_PATH = Path("data/processed/tech_stocks.db")
CREATE_TABLES_SQL_PATH = Path("sql/01_create_tables.sql")
COMPANY_METADATA_PATH = Path("data/raw/company_metadata.csv")
TABLE_NAME = "tech_stocks"
COMPANY_METADATA_TABLE_NAME = "company_metadata"
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
COMPANY_METADATA_COLUMNS = [
    "symbol",
    "company_name",
    "sector",
    "industry",
    "exchange",
    "founded_year",
    "headquarters",
]


def load_clean_data(csv_path):
    """Read and validate the cleaned stock CSV for SQLite loading."""
    data = pd.read_csv(csv_path)
    missing_columns = [column for column in EXPECTED_COLUMNS if column not in data.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns in cleaned data: {missing_columns}")
    return data[EXPECTED_COLUMNS]


def load_company_metadata(csv_path):
    """Read optional company metadata CSV for SQLite loading."""
    metadata_file = Path(csv_path)
    if not metadata_file.exists():
        return None

    metadata = pd.read_csv(metadata_file)
    missing_columns = [
        column for column in COMPANY_METADATA_COLUMNS if column not in metadata.columns
    ]
    if missing_columns:
        raise ValueError(f"Missing required columns in company metadata: {missing_columns}")
    return metadata[COMPANY_METADATA_COLUMNS]


def load_to_sqlite(
    csv_path=CLEAN_INPUT_PATH,
    database_path=DATABASE_PATH,
    sql_path=CREATE_TABLES_SQL_PATH,
    company_metadata_path=COMPANY_METADATA_PATH,
):
    """Create the SQLite database and load the cleaned stock records."""
    csv_file = Path(csv_path)
    database_file = Path(database_path)
    sql_file = Path(sql_path)
    metadata_file = Path(company_metadata_path)

    data = load_clean_data(csv_file)
    company_metadata = load_company_metadata(metadata_file)
    create_tables_sql = sql_file.read_text(encoding="utf-8")

    database_file.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_file) as connection:
        connection.executescript(create_tables_sql)
        data.to_sql(TABLE_NAME, connection, if_exists="append", index=False)
        metadata_row_count = 0
        if company_metadata is not None:
            company_metadata.to_sql(
                COMPANY_METADATA_TABLE_NAME, connection, if_exists="append", index=False
            )
            metadata_row_count = connection.execute(
                f"SELECT COUNT(*) FROM {COMPANY_METADATA_TABLE_NAME}"
            ).fetchone()[0]

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
    if company_metadata is None:
        print(f"Company metadata file not found: {metadata_file}")
    else:
        print(f"Loaded {metadata_row_count} rows into {COMPANY_METADATA_TABLE_NAME}")

    return row_count, unique_symbols, min_date, max_date


def main():
    """Run the SQLite loading workflow from the command line."""
    project_root = Path(__file__).resolve().parents[1]
    csv_path = project_root / CLEAN_INPUT_PATH
    database_path = project_root / DATABASE_PATH
    sql_path = project_root / CREATE_TABLES_SQL_PATH
    company_metadata_path = project_root / COMPANY_METADATA_PATH
    load_to_sqlite(csv_path, database_path, sql_path, company_metadata_path)


if __name__ == "__main__":
    main()
