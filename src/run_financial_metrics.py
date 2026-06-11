"""Generate a stock-level financial metric summary from engineered features."""

from pathlib import Path

import pandas as pd

if __package__:
    from .financial_metrics import create_stock_metric_summary
else:
    from financial_metrics import create_stock_metric_summary


FEATURE_INPUT_PATH = Path("data/processed/stock_features.csv")
METRIC_OUTPUT_PATH = Path("data/processed/stock_metric_summary.csv")


def run_financial_metrics(
    input_path=FEATURE_INPUT_PATH, output_path=METRIC_OUTPUT_PATH
):
    """Load stock features, compute metric summaries, and write the summary CSV."""
    input_file = Path(input_path)
    output_file = Path(output_path)

    df = pd.read_csv(input_file)
    summary = create_stock_metric_summary(df)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(output_file, index=False)

    sorted_summary = summary.sort_values("sharpe_ratio", ascending=False)
    print(sorted_summary.to_string(index=False))
    return summary


def main():
    """Run the financial metric summary workflow from the command line."""
    project_root = Path(__file__).resolve().parents[1]
    input_path = project_root / FEATURE_INPUT_PATH
    output_path = project_root / METRIC_OUTPUT_PATH
    run_financial_metrics(input_path, output_path)


if __name__ == "__main__":
    main()
