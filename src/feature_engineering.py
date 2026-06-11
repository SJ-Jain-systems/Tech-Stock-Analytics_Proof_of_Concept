"""Create model-ready stock price and volume features."""

from pathlib import Path

import numpy as np
import pandas as pd


CLEAN_INPUT_PATH = Path("data/processed/tech_stocks_clean.csv")
FEATURE_OUTPUT_PATH = Path("data/processed/stock_features.csv")
REQUIRED_COLUMNS = ["date", "open", "high", "low", "close", "volume", "symbol"]
RETURN_WINDOWS = [5, 10, 20]
RETURN_LAGS = [1, 2, 3, 5]
MA_WINDOWS = [5, 20, 50]
VOLATILITY_WINDOWS = [10, 20, 50]
MODELING_REQUIRED_COLUMNS = [
    "daily_return",
    "log_return",
    "return_5d",
    "return_10d",
    "return_20d",
    "lag_1_return",
    "lag_2_return",
    "lag_3_return",
    "lag_5_return",
    "ma_5",
    "ma_20",
    "ma_50",
    "close_to_ma20_ratio",
    "rolling_volatility_10",
    "rolling_volatility_20",
    "rolling_volatility_50",
    "volume_change",
    "volume_ma_20",
    "volume_to_ma20_ratio",
    "price_range",
    "price_range_pct",
    "intraday_return",
    "next_day_return",
    "target_next_day_up",
]


def _standardize_columns(df):
    """Return a copy of the input data with lower-case column names."""
    return df.rename(columns={column: column.lower() for column in df.columns})


def validate_input(df):
    """Validate that the cleaned stock dataset has the columns needed for features."""
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")


def create_features(df):
    """Create grouped stock features without leaking calculations across symbols."""
    features = _standardize_columns(df).copy()
    validate_input(features)

    features["date"] = pd.to_datetime(features["date"], errors="coerce")
    for column in ["open", "high", "low", "close", "volume"]:
        features[column] = pd.to_numeric(features[column], errors="coerce")

    input_required_columns = ["date", "symbol", "open", "high", "low", "close", "volume"]
    features = features.dropna(subset=input_required_columns)
    features = features.sort_values(["symbol", "date"]).reset_index(drop=True)

    grouped = features.groupby("symbol", group_keys=False)

    # Return features
    previous_close = grouped["close"].shift(1)
    features["daily_return"] = grouped["close"].pct_change(fill_method=None)
    features["log_return"] = np.log(features["close"] / previous_close)
    for window in RETURN_WINDOWS:
        features[f"return_{window}d"] = grouped["close"].pct_change(
            periods=window, fill_method=None
        )

    # Lag features
    for lag in RETURN_LAGS:
        features[f"lag_{lag}_return"] = grouped["daily_return"].shift(lag)

    # Moving averages
    for window in MA_WINDOWS:
        features[f"ma_{window}"] = grouped["close"].transform(
            lambda series, rolling_window=window: series.rolling(
                rolling_window
            ).mean()
        )
    features["close_to_ma20_ratio"] = features["close"] / features["ma_20"]

    # Volatility
    for window in VOLATILITY_WINDOWS:
        features[f"rolling_volatility_{window}"] = grouped["daily_return"].transform(
            lambda series, rolling_window=window: series.rolling(
                rolling_window
            ).std()
        )

    # Volume
    features["volume_change"] = grouped["volume"].pct_change(fill_method=None)
    features["volume_ma_20"] = grouped["volume"].transform(
        lambda series: series.rolling(20).mean()
    )
    features["volume_to_ma20_ratio"] = features["volume"] / features["volume_ma_20"]

    # Price behavior
    features["price_range"] = features["high"] - features["low"]
    features["price_range_pct"] = features["price_range"] / features["open"]
    features["intraday_return"] = (features["close"] - features["open"]) / features["open"]

    # Target
    next_close = grouped["close"].shift(-1)
    features["next_day_return"] = (next_close / features["close"]) - 1
    features["target_next_day_up"] = (features["next_day_return"] > 0).astype(int)

    features = features.replace([np.inf, -np.inf], np.nan)
    features = features.dropna(subset=MODELING_REQUIRED_COLUMNS).reset_index(drop=True)

    return features


def run_feature_engineering(input_path=CLEAN_INPUT_PATH, output_path=FEATURE_OUTPUT_PATH):
    """Load the cleaned stock CSV, create features, and write the feature CSV."""
    input_file = Path(input_path)
    output_file = Path(output_path)

    df = pd.read_csv(input_file)
    features = create_features(df)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(output_file, index=False)

    print(f"Read {len(df)} cleaned rows from {input_file}")
    print(f"Wrote {len(features)} feature rows to {output_file}")
    return features


def main():
    """Run the feature engineering workflow from the command line."""
    project_root = Path(__file__).resolve().parents[1]
    input_path = project_root / CLEAN_INPUT_PATH
    output_path = project_root / FEATURE_OUTPUT_PATH
    run_feature_engineering(input_path, output_path)


if __name__ == "__main__":
    main()
