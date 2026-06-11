# Tech Stock Risk & Return Analytics

A Python + SQL finance data science project for analyzing historical daily stock data for technology companies. The project starts from the raw dataset at `data/raw/tech_stocks.csv` and is designed to support reproducible data cleaning, SQL analysis, exploratory analytics, visualization, feature engineering, and baseline predictive modeling.

This repository is intentionally initialized without fake outputs or fabricated findings. Reports, figures, processed datasets, and trained models should be generated only after running the analysis workflow on the source data.

## Project Goals

The project focuses on practical risk and return analytics for historical stock market data, including:

- Measuring stock performance through daily returns, cumulative returns, and annualized return metrics.
- Studying volatility with daily return distributions, rolling volatility, and symbol-level risk comparisons.
- Evaluating drawdowns to understand peak-to-trough losses and downside risk.
- Comparing symbols in a portfolio-style workflow using correlations, risk-return tradeoffs, and allocation experiments.
- Engineering features from prices and volume for next-day movement prediction.
- Combining SQL for structured analysis with Python for data science, visualization, and modeling.

## Dataset

The raw input file should be placed at:

```text
data/raw/tech_stocks.csv
```

Expected columns:

| Column | Description |
| --- | --- |
| `Date` | Trading date |
| `Open` | Opening price |
| `High` | Highest intraday price |
| `Low` | Lowest intraday price |
| `Close` | Closing price |
| `Volume` | Shares traded |
| `Symbol` | Stock ticker symbol |

## Repository Structure

```text
.
├── data/
│   ├── raw/          # Original source data, including tech_stocks.csv
│   └── processed/    # Cleaned and feature-engineered datasets
├── sql/              # SQL scripts for validation, aggregation, and analysis
├── notebooks/        # Jupyter notebooks for EDA, modeling, and reporting
├── src/              # Reusable Python package code
├── reports/
│   └── figures/      # Generated charts and visual outputs
├── models/           # Trained model artifacts
├── requirements.txt  # Python dependencies
└── README.md
```

## Data Quality Checks

Use `src/data_profile.py` to profile and validate the raw technology stock dataset before downstream analysis. The script loads `data/raw/tech_stocks.csv` with pandas, parses `Date` as a datetime field, and prints a compact data quality report covering:

- Dataset shape, column names, and pandas dtypes.
- Missing value counts and full duplicate row counts.
- Duplicate `Symbol`/`Date` pair checks to confirm one observation per symbol per trading date.
- Number of unique symbols, date coverage by symbol, and row counts by symbol.
- Validation that `Open`, `High`, `Low`, `Close`, and `Volume` are non-null numeric columns.

The script also writes a symbol-level summary table to `data/processed/data_profile_summary.csv`. Run it from the repository root after placing the raw CSV file in `data/raw/`:

```bash
python src/data_profile.py
```

## Planned Methods

### Data Preparation

- Validate required columns and data types.
- Parse `Date` as a date field.
- Check for missing values, duplicate `Symbol`/`Date` rows, and invalid price or volume values.
- Sort observations by `Symbol` and `Date`.
- Save cleaned analysis-ready files under `data/processed/`.

### SQL Analysis

SQL scripts in `sql/` will be used to answer structured finance questions such as:

- Trading date coverage by symbol.
- Average and total volume by symbol and period.
- Best and worst daily price moves.
- Yearly performance summaries.
- Rolling price and volume calculations where supported by the SQL engine.

### Python Analytics

Python notebooks and reusable modules in `src/` will support:

- Daily and log return calculations.
- Cumulative return analysis.
- Rolling volatility and moving average features.
- Maximum drawdown calculations.
- Correlation analysis across symbols.
- Portfolio-level risk and return comparisons.
- Visualizations of price, volume, volatility, drawdown, and risk-return relationships.

### Predictive Modeling

The modeling workflow will explore next-day movement prediction as a learning-oriented classification task. Potential features include lagged returns, rolling volatility, rolling volume, price range measures, and symbol-level categorical features.

Potential model outputs include:

- Baseline classification metrics.
- Confusion matrices and ROC-AUC scores where appropriate.
- Feature importance or coefficient summaries.
- Saved model artifacts under `models/`.

Models should be evaluated carefully and should not be presented as investment advice or guaranteed trading signals.

## Expected Outputs

Once the workflow is implemented and run, the project is expected to produce:

- Cleaned datasets in `data/processed/`.
- SQL query files documenting core analysis steps.
- Exploratory notebooks with reproducible calculations.
- Figures saved in `reports/figures/`.
- Optional trained model artifacts in `models/`.
- A written summary of stock performance, volatility, drawdown, portfolio behavior, and predictive modeling results.

## Setup

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Place the raw dataset at `data/raw/tech_stocks.csv` before running analysis notebooks or scripts.

## Project Status

Initial project structure and documentation have been created. The next step is to add the raw dataset and begin building the SQL and Python analysis workflow.

## Disclaimer

This project is for educational and portfolio purposes only. It uses historical market data and should not be interpreted as financial advice.
