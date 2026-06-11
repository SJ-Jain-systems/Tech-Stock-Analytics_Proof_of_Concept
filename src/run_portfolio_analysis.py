"""Run the equal-weight portfolio analysis workflow."""

from pathlib import Path

import pandas as pd

if __package__:
    from .portfolio import (
        PORTFOLIO_COMPARISON_OUTPUT_PATH,
        PORTFOLIO_RETURN_OUTPUT_PATH,
        save_portfolio_outputs,
    )
else:
    from portfolio import (
        PORTFOLIO_COMPARISON_OUTPUT_PATH,
        PORTFOLIO_RETURN_OUTPUT_PATH,
        save_portfolio_outputs,
    )


FEATURE_INPUT_PATH = Path("data/processed/stock_features.csv")


def run_portfolio_analysis(input_path=FEATURE_INPUT_PATH):
    """Load engineered returns, run portfolio analysis, and write output CSVs."""
    input_file = Path(input_path)
    df = pd.read_csv(input_file)
    project_root = Path(__file__).resolve().parents[1]
    return_output_path = project_root / PORTFOLIO_RETURN_OUTPUT_PATH
    comparison_output_path = project_root / PORTFOLIO_COMPARISON_OUTPUT_PATH

    portfolio_returns, comparison = save_portfolio_outputs(
        df,
        return_output_path=return_output_path,
        comparison_output_path=comparison_output_path,
    )

    print(f"Read {len(df)} feature rows from {input_file}")
    print(
        "Wrote "
        f"{len(portfolio_returns)} portfolio return rows to "
        f"{return_output_path}"
    )
    print(f"Wrote {len(comparison)} comparison rows to {comparison_output_path}")
    print(comparison.to_string(index=False))
    return portfolio_returns, comparison


def main():
    """Run the portfolio analysis workflow from the command line."""
    project_root = Path(__file__).resolve().parents[1]
    input_path = project_root / FEATURE_INPUT_PATH
    run_portfolio_analysis(input_path)


if __name__ == "__main__":
    main()
