"""Reusable financial performance metrics for stock return analysis."""

import numpy as np
import pandas as pd


REQUIRED_SUMMARY_COLUMNS = ["symbol", "date", "daily_return"]


def _clean_returns(returns):
    """Return a numeric Series with invalid return values removed."""
    numeric_returns = pd.to_numeric(pd.Series(returns), errors="coerce")
    numeric_returns = numeric_returns.replace([np.inf, -np.inf], np.nan)
    return numeric_returns.dropna()


def calculate_cumulative_return(returns):
    """Calculate total compounded return for a sequence of periodic returns."""
    clean_returns = _clean_returns(returns)
    if clean_returns.empty:
        return np.nan
    return (1.0 + clean_returns).prod() - 1.0


def calculate_annualized_return(returns, periods_per_year=252):
    """Calculate compounded annualized return from periodic returns."""
    clean_returns = _clean_returns(returns)
    if clean_returns.empty:
        return np.nan

    cumulative_return = calculate_cumulative_return(clean_returns)
    ending_value = 1.0 + cumulative_return
    if ending_value < 0:
        return np.nan

    years = len(clean_returns) / periods_per_year
    return ending_value ** (1.0 / years) - 1.0


def calculate_annualized_volatility(returns, periods_per_year=252):
    """Calculate annualized volatility from periodic returns."""
    clean_returns = _clean_returns(returns)
    if len(clean_returns) < 2:
        return np.nan
    return clean_returns.std() * np.sqrt(periods_per_year)


def calculate_sharpe_ratio(returns, risk_free_rate=0.0, periods_per_year=252):
    """Calculate annualized Sharpe ratio using an annual risk-free rate."""
    clean_returns = _clean_returns(returns)
    if clean_returns.empty:
        return np.nan

    annualized_volatility = calculate_annualized_volatility(
        clean_returns, periods_per_year=periods_per_year
    )
    if pd.isna(annualized_volatility) or annualized_volatility == 0:
        return np.nan

    annualized_return = calculate_annualized_return(
        clean_returns, periods_per_year=periods_per_year
    )
    return (annualized_return - risk_free_rate) / annualized_volatility


def calculate_sortino_ratio(returns, risk_free_rate=0.0, periods_per_year=252):
    """Calculate annualized Sortino ratio using downside deviation only."""
    clean_returns = _clean_returns(returns)
    if clean_returns.empty:
        return np.nan

    period_risk_free_rate = (1.0 + risk_free_rate) ** (1.0 / periods_per_year) - 1.0
    excess_returns = clean_returns - period_risk_free_rate
    downside_returns = excess_returns[excess_returns < 0]
    if downside_returns.empty:
        return np.nan

    downside_deviation = np.sqrt((downside_returns**2).mean())
    downside_deviation *= np.sqrt(periods_per_year)
    if pd.isna(downside_deviation) or downside_deviation == 0:
        return np.nan

    annualized_return = calculate_annualized_return(
        clean_returns, periods_per_year=periods_per_year
    )
    return (annualized_return - risk_free_rate) / downside_deviation


def calculate_max_drawdown(returns):
    """Calculate the maximum peak-to-trough drawdown from periodic returns."""
    clean_returns = _clean_returns(returns)
    if clean_returns.empty:
        return np.nan

    wealth_index = pd.concat(
        [pd.Series([1.0]), (1.0 + clean_returns).cumprod()], ignore_index=True
    )
    running_peak = wealth_index.cummax()
    drawdowns = (wealth_index / running_peak) - 1.0
    return drawdowns.min()


def calculate_var(returns, confidence_level=0.95):
    """Calculate historical value at risk as the lower-tail return quantile."""
    clean_returns = _clean_returns(returns)
    if clean_returns.empty:
        return np.nan
    if not 0 < confidence_level < 1:
        raise ValueError("confidence_level must be between 0 and 1")

    return clean_returns.quantile(1.0 - confidence_level)


def create_stock_metric_summary(df):
    """Create one row of return performance metrics for each stock symbol."""
    missing_columns = [
        column for column in REQUIRED_SUMMARY_COLUMNS if column not in df.columns
    ]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    metrics = df[REQUIRED_SUMMARY_COLUMNS].copy()
    metrics["date"] = pd.to_datetime(metrics["date"], errors="coerce")
    metrics["daily_return"] = pd.to_numeric(metrics["daily_return"], errors="coerce")
    metrics = metrics.replace([np.inf, -np.inf], np.nan)
    metrics = metrics.dropna(subset=REQUIRED_SUMMARY_COLUMNS)
    metrics = metrics.sort_values(["symbol", "date"])

    summary_rows = []
    for symbol, group in metrics.groupby("symbol"):
        returns = group["daily_return"]
        summary_rows.append(
            {
                "symbol": symbol,
                "start_date": group["date"].min(),
                "end_date": group["date"].max(),
                "observations": len(group),
                "cumulative_return": calculate_cumulative_return(returns),
                "annualized_return": calculate_annualized_return(returns),
                "annualized_volatility": calculate_annualized_volatility(returns),
                "sharpe_ratio": calculate_sharpe_ratio(returns),
                "sortino_ratio": calculate_sortino_ratio(returns),
                "max_drawdown": calculate_max_drawdown(returns),
                "var_95": calculate_var(returns, confidence_level=0.95),
            }
        )

    return pd.DataFrame(
        summary_rows,
        columns=[
            "symbol",
            "start_date",
            "end_date",
            "observations",
            "cumulative_return",
            "annualized_return",
            "annualized_volatility",
            "sharpe_ratio",
            "sortino_ratio",
            "max_drawdown",
            "var_95",
        ],
    )
