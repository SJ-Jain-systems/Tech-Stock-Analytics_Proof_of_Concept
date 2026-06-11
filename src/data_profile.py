"""Profile and validate the raw technology stock dataset."""

from pathlib import Path

import pandas as pd
from pandas.api.types import is_datetime64_any_dtype, is_numeric_dtype


REQUIRED_COLUMNS = ["Date", "Open", "High", "Low", "Close", "Volume", "Symbol"]
NUMERIC_COLUMNS = ["Open", "High", "Low", "Close", "Volume"]


def load_data(path):
    """Load the raw stock CSV and parse Date as a datetime column."""
    data_path = Path(path)
    df = pd.read_csv(data_path)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df


def profile_data(df):
    """Print core profile information for the stock dataset."""
    print("Dataset shape:")
    print(df.shape)

    print("\nColumns and dtypes:")
    print(df.dtypes)

    print("\nMissing value counts:")
    print(df.isna().sum())

    duplicate_rows = df.duplicated().sum()
    print("\nDuplicate row count:")
    print(duplicate_rows)

    duplicate_symbol_dates = df.duplicated(subset=["Symbol", "Date"]).sum()
    print("\nDuplicate Symbol-Date pair count:")
    print(duplicate_symbol_dates)

    unique_symbols = df["Symbol"].nunique(dropna=True)
    print("\nNumber of unique symbols:")
    print(unique_symbols)

    print("\nDate range by Symbol:")
    date_range = (
        df.groupby("Symbol", dropna=False)["Date"]
        .agg(start_date="min", end_date="max")
        .sort_index()
    )
    print(date_range)

    print("\nRow count by Symbol:")
    row_counts = (
        df.groupby("Symbol", dropna=False)
        .size()
        .rename("row_count")
        .sort_index()
    )
    print(row_counts)


def validate_data(df):
    """Validate required columns, Date parsing, and numeric price/volume fields."""
    errors = []

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        errors.append(f"Missing required columns: {missing_columns}")

    if "Date" in df.columns:
        if not is_datetime64_any_dtype(df["Date"]):
            errors.append("Date column must be parsed as datetime.")
        elif df["Date"].isna().any():
            errors.append("Date column contains null or unparseable values.")

    for column in NUMERIC_COLUMNS:
        if column not in df.columns:
            continue
        if df[column].isna().any():
            errors.append(f"{column} contains null values.")
        if not is_numeric_dtype(df[column]):
            errors.append(f"{column} must be numeric.")

    duplicate_symbol_dates = 0
    if {"Symbol", "Date"}.issubset(df.columns):
        duplicate_symbol_dates = df.duplicated(subset=["Symbol", "Date"]).sum()
        if duplicate_symbol_dates:
            errors.append(f"Found {duplicate_symbol_dates} duplicate Symbol-Date pairs.")

    if errors:
        print("\nValidation errors:")
        for error in errors:
            print(f"- {error}")
        raise ValueError("Data validation failed. See validation errors above.")

    print("\nValidation passed:")
    print("Open, High, Low, Close, and Volume are non-null numeric columns.")
    print("Date is parsed as datetime and Symbol-Date pairs are unique.")


def save_summary(df, output_path):
    """Save a symbol-level data quality summary table."""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    summary = (
        df.groupby("Symbol", dropna=False)
        .agg(
            row_count=("Symbol", "size"),
            start_date=("Date", "min"),
            end_date=("Date", "max"),
            missing_dates=("Date", lambda series: series.isna().sum()),
            duplicate_symbol_date_rows=(
                "Date",
                lambda series: df.loc[series.index]
                .duplicated(subset=["Symbol", "Date"])
                .sum(),
            ),
        )
        .reset_index()
        .sort_values("Symbol")
    )

    missing_numeric = (
        df.groupby("Symbol", dropna=False)[NUMERIC_COLUMNS]
        .apply(lambda group: group.isna().sum())
        .reset_index()
        .rename(columns={column: f"missing_{column.lower()}" for column in NUMERIC_COLUMNS})
    )
    summary = summary.merge(missing_numeric, on="Symbol", how="left")

    summary.to_csv(output_file, index=False)
    print(f"\nSaved summary table to {output_file}")


def main():
    """Run the raw data profiling workflow."""
    project_root = Path(__file__).resolve().parents[1]
    input_path = project_root / "data" / "raw" / "tech_stocks.csv"
    output_path = project_root / "data" / "processed" / "data_profile_summary.csv"

    df = load_data(input_path)
    profile_data(df)
    validate_data(df)
    save_summary(df, output_path)


if __name__ == "__main__":
    main()
