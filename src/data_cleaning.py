"""Clean the raw technology stock dataset for downstream analysis."""

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = ["Date", "Open", "High", "Low", "Close", "Volume", "Symbol"]
NUMERIC_COLUMNS = ["open", "high", "low", "close", "volume"]
RAW_INPUT_PATH = Path("data/raw/tech_stocks.csv")
CLEAN_OUTPUT_PATH = Path("data/processed/tech_stocks_clean.csv")


def clean_stock_data(df):
    """Return a cleaned stock DataFrame following the project data rules."""
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    cleaned = df.copy()
    cleaned["Date"] = pd.to_datetime(cleaned["Date"], errors="coerce")

    cleaned = cleaned.sort_values(["Symbol", "Date"])
    cleaned = cleaned.drop_duplicates()
    cleaned = cleaned.drop_duplicates(subset=["Symbol", "Date"], keep="first")

    cleaned = cleaned.rename(columns={column: column.lower() for column in cleaned.columns})

    for column in NUMERIC_COLUMNS:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    cleaned = cleaned.dropna(subset=["date", "symbol", "close"])
    cleaned["trading_year"] = cleaned["date"].dt.year
    cleaned["trading_month"] = cleaned["date"].dt.strftime("%Y-%m")

    return cleaned


def run_cleaning(input_path=RAW_INPUT_PATH, output_path=CLEAN_OUTPUT_PATH):
    """Load the raw CSV, clean it, and write the processed CSV."""
    input_file = Path(input_path)
    output_file = Path(output_path)

    df = pd.read_csv(input_file)
    cleaned = clean_stock_data(df)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(output_file, index=False)

    print(f"Read {len(df)} rows from {input_file}")
    print(f"Wrote {len(cleaned)} cleaned rows to {output_file}")
    return cleaned


def main():
    """Run the stock data cleaning workflow from the command line."""
    project_root = Path(__file__).resolve().parents[1]
    input_path = project_root / RAW_INPUT_PATH
    output_path = project_root / CLEAN_OUTPUT_PATH
    run_cleaning(input_path, output_path)


if __name__ == "__main__":
    main()
