"""Tests for reusable financial metric calculations."""

import numpy as np

from src.financial_metrics import (
    calculate_annualized_volatility,
    calculate_cumulative_return,
    calculate_max_drawdown,
    calculate_var,
)


def test_cumulative_return_calculation():
    returns = [0.10, -0.05, 0.02]

    result = calculate_cumulative_return(returns)

    assert np.isclose(result, (1.10 * 0.95 * 1.02) - 1.0)


def test_annualized_volatility_returns_non_negative_value():
    returns = [0.01, -0.02, 0.015, 0.0]

    result = calculate_annualized_volatility(returns)

    assert result >= 0


def test_max_drawdown_is_less_than_or_equal_to_zero():
    returns = [0.10, -0.20, 0.05]

    result = calculate_max_drawdown(returns)

    assert result <= 0


def test_var_returns_numeric_value():
    returns = [0.01, -0.03, 0.02, -0.01, 0.00]

    result = calculate_var(returns)

    assert isinstance(result, (float, np.floating))
