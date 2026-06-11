"""Tests for grouped stock feature engineering."""

from datetime import date, timedelta

import numpy as np
import pandas as pd

from src.feature_engineering import MODELING_REQUIRED_COLUMNS, create_features


def _sample_stock_data(days=65):
    rows = []
    start = date(2024, 1, 1)
    for symbol, base_price in [("AAA", 100.0), ("BBB", 250.0)]:
        for day in range(days):
            close = base_price + day + (0.1 if symbol == "AAA" else 0.2)
            rows.append(
                {
                    "date": start + timedelta(days=day),
                    "open": close - 0.5,
                    "high": close + 1.0,
                    "low": close - 1.0,
                    "close": close,
                    "volume": 1_000_000 + day * 100 + (0 if symbol == "AAA" else 50),
                    "symbol": symbol,
                }
            )
    return pd.DataFrame(rows)


def test_feature_engineering_does_not_mix_symbols():
    features = create_features(_sample_stock_data())
    original = _sample_stock_data()

    for symbol in ["AAA", "BBB"]:
        first_symbol_row = features[features["symbol"] == symbol].iloc[0]
        symbol_history = original[original["symbol"] == symbol].sort_values("date")
        expected_lag = symbol_history["close"].pct_change().iloc[49]

        assert first_symbol_row["date"] == pd.Timestamp(symbol_history.iloc[50]["date"])
        assert np.isclose(first_symbol_row["lag_1_return"], expected_lag)


def test_target_next_day_up_is_only_zero_or_one():
    features = create_features(_sample_stock_data())

    assert set(features["target_next_day_up"].unique()).issubset({0, 1})


def test_required_feature_columns_exist_after_feature_engineering():
    features = create_features(_sample_stock_data())

    for column in MODELING_REQUIRED_COLUMNS:
        assert column in features.columns
