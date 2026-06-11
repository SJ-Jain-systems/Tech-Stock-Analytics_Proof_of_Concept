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


## Feature Engineering

Use `src/feature_engineering.py` after cleaning the raw dataset to create model-ready stock features from `data/processed/tech_stocks_clean.csv` and write them to `data/processed/stock_features.csv`:

```bash
python src/feature_engineering.py
```

The feature engineering workflow sorts observations by `symbol` and `date`, applies all rolling, lagged, and target calculations within `groupby("symbol")`, and drops only rows missing required modeling columns caused by lag, rolling-window, or next-day target calculations. Created features include:

- Return features: `daily_return`, `log_return`, `return_5d`, `return_10d`, and `return_20d`.
- Lag features: `lag_1_return`, `lag_2_return`, `lag_3_return`, and `lag_5_return`.
- Moving averages: `ma_5`, `ma_20`, `ma_50`, and `close_to_ma20_ratio`.
- Volatility features: `rolling_volatility_10`, `rolling_volatility_20`, and `rolling_volatility_50`.
- Volume features: `volume_change`, `volume_ma_20`, and `volume_to_ma20_ratio`.
- Price behavior features: `price_range`, `price_range_pct`, and `intraday_return`.
- Target columns: `next_day_return` and `target_next_day_up`, where `target_next_day_up` equals `1` when the next-day return is positive and `0` otherwise.


## Portfolio Analysis

Use `src/run_portfolio_analysis.py` after feature engineering to test a simple equal-weight portfolio built from the available stock return series in `data/processed/stock_features.csv`:

```bash
python src/run_portfolio_analysis.py
```

The workflow pivots the engineered `daily_return` values into a date-indexed return matrix with one column per symbol, then calculates the portfolio daily return as the average return across all symbols with valid data on each trading date. This means each available stock contributes the same weight for that date instead of weighting larger companies more heavily.

The analysis saves two portfolio outputs under `data/processed/`:

- `equal_weight_portfolio_returns.csv` with the portfolio daily return and compounded cumulative return by date.
- `portfolio_comparison.csv` with the equal-weight portfolio metrics stacked against individual stock metrics, including cumulative return, annualized return, annualized volatility, Sharpe ratio, Sortino ratio, maximum drawdown, and 95% historical value at risk.

Diversification is being tested because a basket of stocks can reduce company-specific risk when individual stock returns do not move perfectly together. Comparing the equal-weight portfolio against each stock shows whether spreading capital evenly across the symbols improves the risk-return profile, reduces volatility, limits drawdowns, or provides a smoother return path than holding a single technology stock.

## Planned Methods

### Data Preparation

- Validate required columns and data types.
- Parse `Date` as a date field.
- Check for missing values, duplicate `Symbol`/`Date` rows, and invalid price or volume values.
- Sort observations by `Symbol` and `Date`.
- Save cleaned analysis-ready files under `data/processed/`.

### SQL Analysis

SQL scripts in `sql/` provide SQLite-compatible table setup, validation, and repeatable analysis queries:

- `sql/01_create_tables.sql` rebuilds the `tech_stocks` table used by the SQLite loader.
- `sql/02_data_quality_checks.sql` validates the loaded table with total row counts, unique symbol counts, symbol-level date coverage, duplicate `symbol`/`date` checks, missing close price checks, and trading day counts by symbol.
- `sql/03_price_volume_summary.sql` summarizes average close prices, average volume, highest-volume trading days, highest-volume day per symbol with window functions, average daily price ranges, and average daily range percentages.
- `sql/04_return_analysis.sql` calculates daily returns with `LAG(close)`, average daily returns, best and worst single-day returns, monthly returns, and yearly returns using CTEs and window functions.

Run these scripts against the SQLite database created by `src/load_to_sqlite.py`, for example:

```bash
sqlite3 data/processed/tech_stocks.db < sql/02_data_quality_checks.sql
sqlite3 data/processed/tech_stocks.db < sql/03_price_volume_summary.sql
sqlite3 data/processed/tech_stocks.db < sql/04_return_analysis.sql
```

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

Clean the raw stock dataset and write `data/processed/tech_stocks_clean.csv` with:

```bash
python src/data_cleaning.py
```

## SQL Database Setup

After creating `data/processed/tech_stocks_clean.csv`, build the local SQLite database and load the cleaned stock records with:

```bash
python src/load_to_sqlite.py
```

The loader creates `data/processed/tech_stocks.db`, rebuilds the `tech_stocks` table from `sql/01_create_tables.sql`, loads the cleaned CSV data, and prints the loaded row count, unique symbol count, and database date range.

## Project Status

Initial project structure and documentation have been created. The next step is to add the raw dataset and begin building the SQL and Python analysis workflow.

## Disclaimer

This project is for educational and portfolio purposes only. It uses historical market data and should not be interpreted as financial advice.
