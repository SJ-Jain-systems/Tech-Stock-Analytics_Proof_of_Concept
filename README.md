# Tech Stock Price & Volume Analytics

## 1. Project Overview

Tech Stock Price & Volume Analytics is an end-to-end data analytics and data science portfolio project for analyzing historical daily price and volume behavior across major technology and technology-adjacent public companies. The project combines reproducible Python pipelines, SQLite-based analytical querying, financial risk/return metrics, portfolio comparison, and baseline predictive modeling.

The workflow is designed to move from raw market data to analysis-ready outputs in a transparent sequence:

1. Clean raw OHLCV stock data.
2. Load the cleaned dataset and company reference data into SQLite.
3. Engineer return, volatility, moving-average, volume, and next-day target features.
4. Compute stock-level financial performance metrics.
5. Compare individual stocks against an equal-weight portfolio.
6. Train baseline classifiers to test whether engineered price/volume features contain predictive signal for next-day direction.

This repository intentionally separates reproducible code from generated artifacts. Processed CSV files, SQLite databases, figures, and model artifacts are generated locally by running the pipeline rather than being treated as hard-coded findings.

## 2. Business / Research Questions

The project is structured around practical questions that an analyst, data scientist, or investment research team might ask when studying historical technology stock behavior:

- How clean and complete is the raw daily stock dataset by symbol and date?
- What are the long-term price and volume patterns across the covered companies?
- Which symbols show higher or lower historical volatility?
- How do daily, monthly, and yearly returns vary by company?
- Which companies experienced the largest downside risk as measured by maximum drawdown and historical value at risk?
- Do simple risk-adjusted metrics such as Sharpe and Sortino ratios meaningfully differentiate stocks?
- Does an equal-weight portfolio provide a smoother risk/return profile than holding individual stocks?
- Do lagged returns, moving averages, volatility, intraday price behavior, and volume features contain measurable signal for next-day price direction?
- How can SQL and Python be combined into a clean, auditable analytics workflow?

The predictive modeling section is framed as a signal-detection exercise, not as a promise of profitable trading performance.

## 3. Dataset

### Raw Stock Data

The main raw input file expected by the pipeline is:

```text
data/raw/tech_stocks.csv
```

The cleaning script expects the raw stock file to contain these columns:

| Column | Description |
| --- | --- |
| `Date` | Trading date. |
| `Open` | Opening price for the trading day. |
| `High` | Highest traded price during the day. |
| `Low` | Lowest traded price during the day. |
| `Close` | Closing price for the trading day. |
| `Volume` | Number of shares traded. |
| `Symbol` | Stock ticker symbol. |

During cleaning, column names are standardized to lowercase, dates are parsed, core price/volume fields are coerced to numeric values, missing required fields are removed, duplicate symbol-date observations are dropped, and trading year/month fields are added.

### Company Metadata

The repository also includes a small reference table at:

```text
data/raw/company_metadata.csv
```

This file maps covered ticker symbols to company-level context, including company name, sector, industry, exchange, founding year, and headquarters. It is loaded into SQLite when available and supports joined SQL analysis.

### Generated Data

Pipeline outputs are written under `data/processed/`. These generated files are intentionally ignored by Git, so final numerical results should be reproduced by running the project locally on the raw dataset instead of being copied from the README.

## 4. Methods

The project uses a layered analytics workflow:

- **Data cleaning:** Standardize schema, validate required columns, parse dates, remove unusable rows, remove duplicate symbol-date records, and create calendar helper fields.
- **Relational analysis:** Load cleaned stock data and company metadata into SQLite for repeatable SQL checks, aggregations, joins, and window-function return analysis.
- **Feature engineering:** Create lagged return, rolling return, moving-average, volatility, volume, intraday, and next-day target features by symbol.
- **Exploratory analysis:** Use notebooks to inspect data quality, price behavior, return distributions, risk/return patterns, portfolio behavior, and modeling outputs.
- **Financial metrics:** Summarize cumulative return, annualized return, annualized volatility, Sharpe ratio, Sortino ratio, maximum drawdown, and 95% historical value at risk.
- **Portfolio analysis:** Build a simple equal-weight portfolio from available return series and compare its metrics against the individual symbols.
- **Predictive modeling:** Train baseline classification models with a chronological train/test split to evaluate whether historical price/volume features contain next-day directional signal.

## 5. Repository Structure

```text
.
├── data/
│   ├── raw/
│   │   ├── company_metadata.csv
│   │   └── tech_stocks.csv              # Expected local raw stock input
│   └── processed/                       # Generated CSV and SQLite outputs
├── models/                              # Generated model artifacts
├── notebooks/
│   ├── 01_data_cleaning.ipynb
│   ├── 02_exploratory_analysis.ipynb
│   ├── 03_risk_return_analysis.ipynb
│   ├── 04_portfolio_analysis.ipynb
│   └── 05_predictive_modeling.ipynb
├── reports/
│   └── figures/                         # Generated visualizations
├── sql/
│   ├── 01_create_tables.sql
│   ├── 02_data_quality_checks.sql
│   ├── 03_price_volume_summary.sql
│   ├── 04_return_analysis.sql
│   └── 05_company_metadata_joins.sql
├── src/
│   ├── data_cleaning.py
│   ├── data_profile.py
│   ├── feature_engineering.py
│   ├── financial_metrics.py
│   ├── load_to_sqlite.py
│   ├── modeling.py
│   ├── portfolio.py
│   ├── run_financial_metrics.py
│   └── run_portfolio_analysis.py
├── requirements.txt
└── README.md
```

## 6. SQL Analysis

SQLite is used as the relational layer for structured analysis. The script `src/load_to_sqlite.py` reads the cleaned stock data from `data/processed/tech_stocks_clean.csv`, creates the SQLite database at `data/processed/tech_stocks.db`, loads the main `tech_stocks` table, and loads `company_metadata` when the metadata CSV is present.

The SQL directory contains focused scripts:

| SQL File | Purpose |
| --- | --- |
| `sql/01_create_tables.sql` | Defines the `tech_stocks` and `company_metadata` tables. |
| `sql/02_data_quality_checks.sql` | Checks row counts, symbol counts, date ranges, duplicate symbol-date rows, missing close prices, and trading-day counts. |
| `sql/03_price_volume_summary.sql` | Summarizes average close price, average volume, high-volume days, highest-volume day per symbol, and daily price ranges. |
| `sql/04_return_analysis.sql` | Uses window functions to calculate daily returns, average daily returns, best/worst single-day returns, monthly returns, and yearly returns. |
| `sql/05_company_metadata_joins.sql` | Joins stock records with company metadata for company, sector, industry, exchange, and headquarters context. |

These scripts are written to support reproducible investigation rather than one-off manual analysis.

## 7. Feature Engineering

`src/feature_engineering.py` converts the cleaned dataset into a modeling-ready feature table at:

```text
data/processed/stock_features.csv
```

Feature creation is performed independently within each symbol after sorting by symbol and date. This prevents leakage across companies when calculating lagged and rolling fields.

Engineered features include:

- **Return features:** `daily_return`, `log_return`, `return_5d`, `return_10d`, `return_20d`.
- **Lag features:** `lag_1_return`, `lag_2_return`, `lag_3_return`, `lag_5_return`.
- **Moving averages:** `ma_5`, `ma_20`, `ma_50`, `close_to_ma20_ratio`.
- **Volatility features:** `rolling_volatility_10`, `rolling_volatility_20`, `rolling_volatility_50`.
- **Volume features:** `volume_change`, `volume_ma_20`, `volume_to_ma20_ratio`.
- **Intraday price behavior:** `price_range`, `price_range_pct`, `intraday_return`.
- **Prediction target:** `next_day_return` and binary `target_next_day_up`.

Rows that cannot support required modeling fields because of lag, rolling-window, or next-day target calculations are dropped from the final feature output.

## 8. Exploratory Data Analysis

Exploratory analysis is supported through the notebooks in `notebooks/` and through generated pipeline outputs. The EDA workflow is intended to examine:

- Dataset shape, schema, and data quality issues.
- Date coverage and row counts by stock symbol.
- Price trends and volume trends over time.
- Daily return distributions and outlier behavior.
- Rolling volatility patterns.
- Cumulative return paths by symbol.
- Correlations across stock return series.
- Drawdown patterns and downside risk.
- Differences between individual-stock behavior and portfolio-level behavior.

The README does not list final EDA conclusions because generated processed outputs are not currently committed to the repository. Analysts should run the pipeline and notebooks to produce reproducible results from the raw data.

## 9. Financial Metrics

`src/run_financial_metrics.py` reads `data/processed/stock_features.csv` and writes a stock-level summary to:

```text
data/processed/stock_metric_summary.csv
```

The metrics are calculated from daily returns and include:

| Metric | Interpretation |
| --- | --- |
| `cumulative_return` | Total compounded return over the available period. |
| `annualized_return` | Return scaled to a 252-trading-day year. |
| `annualized_volatility` | Standard deviation of daily returns scaled to a 252-trading-day year. |
| `sharpe_ratio` | Excess annualized return divided by annualized volatility, using a default risk-free rate of 0. |
| `sortino_ratio` | Excess annualized return divided by annualized downside deviation. |
| `max_drawdown` | Largest peak-to-trough cumulative decline. |
| `var_95` | 95% historical value at risk based on the lower tail of daily returns. |

These metrics support risk/return comparison but should not be interpreted as forecasts of future performance.

## 10. Portfolio Analysis

`src/run_portfolio_analysis.py` evaluates a simple equal-weight portfolio using the engineered daily return series. The portfolio return for each date is calculated as the average return across symbols with valid data on that date.

The workflow writes two files:

```text
data/processed/equal_weight_portfolio_returns.csv
data/processed/portfolio_comparison.csv
```

The first file contains the portfolio daily return and compounded cumulative return by date. The second file compares the equal-weight portfolio against individual stock metrics using the same financial metric framework.

The purpose of this section is to evaluate diversification effects in a transparent way: if individual stocks do not move perfectly together, a basket can potentially reduce company-specific volatility and drawdown risk. The project does not assume the equal-weight portfolio is optimal; it is a clear baseline for comparison.

## 11. Predictive Modeling

`src/modeling.py` trains baseline classifiers to test whether engineered historical price and volume features contain measurable signal for next-day directional movement.

The modeling target is:

```text
target_next_day_up
```

This target equals `1` when the next-day return is positive and `0` otherwise.

The modeling workflow uses a chronological train/test split rather than a random split, which better reflects the time-ordered nature of financial data. It trains baseline models, evaluates out-of-sample classification performance, and writes:

```text
data/processed/model_comparison.csv
data/processed/feature_importance.csv
models/logistic_regression.joblib
models/random_forest.joblib
```

Model evaluation metrics include accuracy, precision, recall, F1 score, ROC AUC when available, and the number of test observations.

The predictive model is designed to test whether price/volume features contain signal. It is not designed to guarantee profitable trading, and it does not include transaction costs, slippage, position sizing, execution constraints, taxes, or live-market validation.

## 12. How to Run

### 1. Set Up the Environment

From the repository root, create and activate a Python environment, then install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

### 2. Add the Raw Stock Dataset

Place the raw stock CSV at:

```text
data/raw/tech_stocks.csv
```

The included `data/raw/company_metadata.csv` can remain in place for SQL metadata joins.

### 3. Run the Pipeline

Run the command-line workflow in this order:

```bash
python src/data_cleaning.py
python src/load_to_sqlite.py
python src/feature_engineering.py
python src/run_financial_metrics.py
python src/run_portfolio_analysis.py
python src/modeling.py
```

### 4. Optional Data Profiling

Before or after cleaning, you can run a standalone raw-data profiling script:

```bash
python src/data_profile.py
```

This writes `data/processed/data_profile_summary.csv` and prints compact validation details.

### 5. Optional SQL Exploration

After running `python src/load_to_sqlite.py`, open `data/processed/tech_stocks.db` with a SQLite client and run the scripts in the `sql/` directory.

Example:

```bash
sqlite3 data/processed/tech_stocks.db < sql/02_data_quality_checks.sql
sqlite3 data/processed/tech_stocks.db < sql/03_price_volume_summary.sql
sqlite3 data/processed/tech_stocks.db < sql/04_return_analysis.sql
sqlite3 data/processed/tech_stocks.db < sql/05_company_metadata_joins.sql
```

## 13. Expected Outputs

After the full workflow completes, expected generated outputs include:

| Output | Created By | Description |
| --- | --- | --- |
| `data/processed/tech_stocks_clean.csv` | `src/data_cleaning.py` | Cleaned, standardized stock dataset. |
| `data/processed/tech_stocks.db` | `src/load_to_sqlite.py` | SQLite database with stock and metadata tables. |
| `data/processed/stock_features.csv` | `src/feature_engineering.py` | Feature-engineered dataset for metrics and modeling. |
| `data/processed/stock_metric_summary.csv` | `src/run_financial_metrics.py` | Stock-level risk/return metric summary. |
| `data/processed/equal_weight_portfolio_returns.csv` | `src/run_portfolio_analysis.py` | Daily and cumulative returns for the equal-weight portfolio. |
| `data/processed/portfolio_comparison.csv` | `src/run_portfolio_analysis.py` | Individual stock metrics compared with the equal-weight portfolio. |
| `data/processed/model_comparison.csv` | `src/modeling.py` | Classification metric comparison for trained baseline models. |
| `data/processed/feature_importance.csv` | `src/modeling.py` | Model-derived feature importance summary when available. |
| `models/logistic_regression.joblib` | `src/modeling.py` | Saved logistic regression pipeline. |
| `models/random_forest.joblib` | `src/modeling.py` | Saved random forest pipeline. |

Because processed outputs are generated artifacts, numerical values should be taken from local pipeline outputs rather than from this README.

## 14. Limitations

Important limitations include:

- The project depends on the availability and quality of the local raw stock CSV.
- The pipeline uses historical daily OHLCV data only; it does not include fundamentals, earnings, analyst estimates, macroeconomic data, news, sentiment, options data, or intraday order-book information.
- Financial metrics are backward-looking and may not represent future market behavior.
- The default risk-free rate used in Sharpe and Sortino calculations is zero unless changed in code.
- The equal-weight portfolio is a simple benchmark, not a portfolio optimization model.
- The predictive model uses historical engineered features and does not account for transaction costs, slippage, liquidity limits, market impact, taxes, or execution timing.
- Classification metrics do not automatically translate into profitable trading performance.
- The model training workflow is a baseline approach and should not be treated as production-grade live trading infrastructure.

## 15. Future Improvements

Potential extensions include:

- Add automated tests for cleaning, feature engineering, metric calculations, and modeling outputs.
- Add richer visual reporting and export key figures to `reports/figures/`.
- Add walk-forward validation or expanding-window backtesting for time-series model evaluation.
- Include transaction costs, slippage assumptions, and position-sizing rules in strategy simulations.
- Compare additional models such as gradient boosting, calibrated classifiers, and regularized linear models.
- Add benchmark comparison against broad market ETFs or sector indexes.
- Incorporate fundamentals, earnings dates, macro variables, sentiment, or news features.
- Add portfolio optimization methods such as minimum variance, maximum Sharpe, and risk parity.
- Add data validation with schema checks and pipeline tests in continuous integration.
- Package the workflow as a command-line application or reproducible notebook report.

## 16. Disclaimer

This project is for educational, analytical, and portfolio demonstration purposes only. It is not investment advice, financial advice, trading advice, or a recommendation to buy, sell, or hold any security.

Historical performance does not guarantee future results. The predictive modeling workflow is designed to test whether engineered price and volume features contain statistical signal for next-day direction; it is not designed to guarantee profitable trading or live investment performance. Anyone making financial decisions should consult qualified professionals and perform independent due diligence.
