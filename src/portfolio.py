"""Equal-weight portfolio construction and comparison utilities."""

from pathlib import Path

import numpy as np
import pandas as pd

if __package__:
    from .financial_metrics import (
        calculate_annualized_return,
        calculate_annualized_volatility,
        calculate_cumulative_return,
        calculate_max_drawdown,
        calculate_sharpe_ratio,
        calculate_sortino_ratio,
        calculate_var,
        create_stock_metric_summary,
    )
else:
    from financial_metrics import (
        calculate_annualized_return,
        calculate_annualized_volatility,
        calculate_cumulative_return,
        calculate_max_drawdown,
        calculate_sharpe_ratio,
        calculate_sortino_ratio,
        calculate_var,
        create_stock_metric_summary,
    )


REQUIRED_RETURN_COLUMNS = ["date", "symbol", "daily_return"]
PORTFOLIO_RETURN_OUTPUT_PATH = Path(
    "data/processed/equal_weight_portfolio_returns.csv"
)
PORTFOLIO_COMPARISON_OUTPUT_PATH = Path("data/processed/portfolio_comparison.csv")
PORTFOLIO_SYMBOL = "EQUAL_WEIGHT_PORTFOLIO"


def _standardize_columns(df):
    """Return a copy of the input data with lower-case column names."""
    return df.rename(columns={column: column.lower() for column in df.columns})


def _prepare_return_data(df):
    """Validate and clean stock return data for portfolio calculations."""
    returns = _standardize_columns(df).copy()
    missing_columns = [
        column for column in REQUIRED_RETURN_COLUMNS if column not in returns.columns
    ]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    returns = returns[REQUIRED_RETURN_COLUMNS].copy()
    returns["date"] = pd.to_datetime(returns["date"], errors="coerce")
    returns["daily_return"] = pd.to_numeric(
        returns["daily_return"], errors="coerce"
    )
    returns = returns.replace([np.inf, -np.inf], np.nan)
    returns = returns.dropna(subset=REQUIRED_RETURN_COLUMNS)
    return returns.sort_values(["date", "symbol"])


def create_return_matrix(df):
    """Create a date-indexed return matrix with one daily-return column per symbol."""
    returns = _prepare_return_data(df)
    return_matrix = returns.pivot_table(
        index="date",
        columns="symbol",
        values="daily_return",
        aggfunc="mean",
    )
    return return_matrix.sort_index()


def calculate_equal_weight_portfolio_returns(return_matrix):
    """Calculate equal-weight portfolio returns across available symbols by date."""
    numeric_returns = return_matrix.apply(pd.to_numeric, errors="coerce")
    portfolio_returns = numeric_returns.mean(axis=1, skipna=True)
    portfolio_returns = portfolio_returns.dropna()
    portfolio_returns.name = "daily_return"
    return portfolio_returns


def calculate_portfolio_cumulative_returns(portfolio_returns):
    """Calculate compounded cumulative returns from portfolio daily returns."""
    clean_returns = pd.to_numeric(
        pd.Series(portfolio_returns), errors="coerce"
    ).replace([np.inf, -np.inf], np.nan)
    clean_returns = clean_returns.dropna()
    cumulative_returns = (1.0 + clean_returns).cumprod() - 1.0
    cumulative_returns.name = "cumulative_return"
    return cumulative_returns


def _create_portfolio_metric_summary(portfolio_returns):
    """Create a one-row metric summary for the equal-weight portfolio."""
    clean_returns = pd.to_numeric(
        pd.Series(portfolio_returns), errors="coerce"
    ).replace([np.inf, -np.inf], np.nan)
    clean_returns = clean_returns.dropna()

    if clean_returns.empty:
        start_date = pd.NaT
        end_date = pd.NaT
    else:
        start_date = clean_returns.index.min()
        end_date = clean_returns.index.max()

    return pd.DataFrame(
        [
            {
                "symbol": PORTFOLIO_SYMBOL,
                "start_date": start_date,
                "end_date": end_date,
                "observations": len(clean_returns),
                "cumulative_return": calculate_cumulative_return(clean_returns),
                "annualized_return": calculate_annualized_return(clean_returns),
                "annualized_volatility": calculate_annualized_volatility(clean_returns),
                "sharpe_ratio": calculate_sharpe_ratio(clean_returns),
                "sortino_ratio": calculate_sortino_ratio(clean_returns),
                "max_drawdown": calculate_max_drawdown(clean_returns),
                "var_95": calculate_var(clean_returns, confidence_level=0.95),
                "asset_type": "portfolio",
            }
        ]
    )


def compare_portfolio_to_stocks(df):
    """Compare equal-weight portfolio metrics against individual stock metrics."""
    returns = _prepare_return_data(df)
    return_matrix = create_return_matrix(returns)
    portfolio_returns = calculate_equal_weight_portfolio_returns(return_matrix)

    stock_summary = create_stock_metric_summary(returns)
    if not stock_summary.empty:
        stock_summary = stock_summary.copy()
        stock_summary["asset_type"] = "stock"

    portfolio_summary = _create_portfolio_metric_summary(portfolio_returns)
    comparison = pd.concat([portfolio_summary, stock_summary], ignore_index=True)

    ordered_columns = [
        "asset_type",
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
    ]
    return comparison[ordered_columns]


def save_portfolio_outputs(
    df,
    return_output_path=PORTFOLIO_RETURN_OUTPUT_PATH,
    comparison_output_path=PORTFOLIO_COMPARISON_OUTPUT_PATH,
):
    """Save equal-weight portfolio returns and stock comparison outputs as CSVs."""
    return_matrix = create_return_matrix(df)
    portfolio_returns = calculate_equal_weight_portfolio_returns(return_matrix)
    cumulative_returns = calculate_portfolio_cumulative_returns(portfolio_returns)
    comparison = compare_portfolio_to_stocks(df)

    portfolio_output = pd.DataFrame(
        {
            "date": portfolio_returns.index,
            "daily_return": portfolio_returns.values,
            "cumulative_return": cumulative_returns.reindex(
                portfolio_returns.index
            ).values,
        }
    )

    return_output_file = Path(return_output_path)
    comparison_output_file = Path(comparison_output_path)

    return_output_file.parent.mkdir(parents=True, exist_ok=True)
    comparison_output_file.parent.mkdir(parents=True, exist_ok=True)
    portfolio_output.to_csv(return_output_file, index=False)
    comparison.to_csv(comparison_output_file, index=False)

    return portfolio_output, comparison
