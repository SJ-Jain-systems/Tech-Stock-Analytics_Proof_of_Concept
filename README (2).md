# Tech Stock Performance Analytics

A data analytics and data science project analyzing long-run price behavior, trading volume, volatility, and risk-adjusted performance across major technology stocks.

This repository starts with a historical stock price dataset covering **AAPL, AMZN, FB, GOOG, MSFT, NFLX, and NVDA** from **1998-01-02 to 2021-06-14**. The project is designed to combine SQL-based analysis, Python exploratory data analysis, statistical feature engineering, and optional predictive modeling.

The goal is not to “predict the market perfectly.” The goal is to build a clean, realistic analytics workflow that answers practical questions about historical tech stock performance.

---

## Project Overview

Technology stocks have experienced major growth, crashes, recoveries, stock splits, and changing trading behavior over the past two decades. This project analyzes those patterns using daily historical stock data.

The project focuses on questions such as:

- Which tech stocks produced the strongest long-term returns?
- Which stocks had the highest volatility?
- How did trading volume change over time?
- Which companies had the largest drawdowns?
- How did each stock perform during major market periods?
- Are daily returns, volume, and volatility useful for forecasting short-term price movement?
- How do SQL and Python workflows complement each other in a financial analytics project?

---

## Dataset

The initial dataset is:

```text
tech_stocks.csv
```

The file contains **32,224 daily stock records** for 7 major technology companies.

### Companies Included

| Symbol | Company |
|---|---|
| AAPL | Apple |
| AMZN | Amazon |
| FB | Meta / Facebook |
| GOOG | Alphabet / Google |
| MSFT | Microsoft |
| NFLX | Netflix |
| NVDA | Nvidia |

### Date Range

```text
1998-01-02 to 2021-06-14
```

### Columns

| Column | Description |
|---|---|
| `symbol` | Stock ticker symbol |
| `date` | Trading date |
| `open` | Opening stock price |
| `high` | Highest price during the trading day |
| `low` | Lowest price during the trading day |
| `close` | Closing stock price |
| `close_adjusted` | Adjusted closing price accounting for splits/dividends |
| `volume` | Number of shares traded |
| `split_coefficient` | Stock split adjustment factor |
| `Unnamed: 0` | Original index column from the CSV; should be dropped during cleaning |

---

## Main Project Objectives

This project is organized around four main goals.

### 1. Build a Clean Analytics Dataset

The raw CSV needs basic cleaning before analysis:

- Drop the unnecessary `Unnamed: 0` column.
- Convert `date` to a proper date format.
- Check for missing values.
- Check for duplicate `symbol` + `date` rows.
- Sort observations by symbol and date.
- Use `close_adjusted` for return calculations because it accounts for stock splits.

### 2. Use SQL for Core Financial Analysis

SQL will be used to answer structured business and analytics questions, including:

- Average annual closing price by stock.
- Total trading volume by year.
- Best and worst daily returns.
- Rolling price movement.
- Highest-volume trading days.
- Yearly return by company.
- Drawdown analysis.
- Comparison of companies by long-term performance.

### 3. Use Python for EDA and Visualization

Python will be used for deeper analysis and visual storytelling:

- Price trends over time.
- Daily return distributions.
- Rolling volatility.
- Volume trends.
- Correlation between stock returns.
- Cumulative return comparison.
- Drawdown charts.
- Risk-return scatterplots.

### 4. Add a Data Science Component

The project can be extended beyond descriptive analytics by building simple models, such as:

- Predicting whether the next trading day closes higher or lower.
- Predicting next-day return direction using lagged returns and volume features.
- Clustering stocks based on volatility, return, and drawdown behavior.
- Comparing risk-adjusted performance using Sharpe-like metrics.

---

## Suggested Repository Structure

```text
tech-stock-performance-analytics/
│
├── data/
│   ├── raw/
│   │   └── tech_stocks.csv
│   │
│   ├── processed/
│   │   └── tech_stocks_clean.csv
│   │
│   └── reference/
│       └── company_metadata.csv
│
├── notebooks/
│   ├── 01_data_cleaning.ipynb
│   ├── 02_sql_analysis.ipynb
│   ├── 03_exploratory_data_analysis.ipynb
│   ├── 04_feature_engineering.ipynb
│   └── 05_modeling.ipynb
│
├── sql/
│   ├── 01_create_tables.sql
│   ├── 02_cleaning_checks.sql
│   ├── 03_stock_performance_queries.sql
│   └── 04_feature_queries.sql
│
├── reports/
│   └── figures/
│
├── src/
│   ├── data_cleaning.py
│   ├── feature_engineering.py
│   └── visualization.py
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

## SQL Setup

This project can use SQLite, PostgreSQL, or DuckDB. DuckDB is a strong option because it works directly with CSV files and integrates well with Python notebooks.

### Recommended SQL Engine

```text
DuckDB
```

DuckDB is simple, fast, and well-suited for local analytics projects.

Install with:

```bash
pip install duckdb
```

---

## SQL Table Design

The main table can be created directly from the CSV.

```sql
CREATE TABLE tech_stocks AS
SELECT
    symbol,
    CAST(date AS DATE) AS date,
    open,
    high,
    low,
    close,
    close_adjusted,
    volume,
    split_coefficient
FROM read_csv_auto('data/raw/tech_stocks.csv');
```

The `Unnamed: 0` column is intentionally excluded because it is only an old index column.

---

## Is Another CSV Necessary?

A second CSV is **not required**. The current dataset is enough for a solid SQL and Python analytics project.

However, a second small reference table would make the SQL portion stronger because it would allow joins, grouping by company attributes, and more realistic database design.

Recommended optional file:

```text
company_metadata.csv
```

Suggested structure:

| symbol | company_name | sector | industry | exchange | founded_year |
|---|---|---|---|---|---|
| AAPL | Apple | Technology | Consumer Electronics | NASDAQ | 1976 |
| AMZN | Amazon | Consumer Discretionary | Internet Retail | NASDAQ | 1994 |
| FB | Meta Platforms | Communication Services | Social Media | NASDAQ | 2004 |
| GOOG | Alphabet | Communication Services | Internet Services | NASDAQ | 1998 |
| MSFT | Microsoft | Technology | Software | NASDAQ | 1975 |
| NFLX | Netflix | Communication Services | Streaming Entertainment | NASDAQ | 1997 |
| NVDA | Nvidia | Technology | Semiconductors | NASDAQ | 1993 |

If this file is added, the database can include a second table:

```sql
CREATE TABLE company_metadata (
    symbol TEXT PRIMARY KEY,
    company_name TEXT,
    sector TEXT,
    industry TEXT,
    exchange TEXT,
    founded_year INTEGER
);
```

This would support queries such as:

```sql
SELECT
    m.sector,
    COUNT(DISTINCT s.symbol) AS number_of_stocks,
    AVG(s.close_adjusted) AS avg_adjusted_close,
    SUM(s.volume) AS total_volume
FROM tech_stocks s
JOIN company_metadata m
    ON s.symbol = m.symbol
GROUP BY m.sector
ORDER BY total_volume DESC;
```

---

## Example SQL Questions

### 1. How many records are available for each stock?

```sql
SELECT
    symbol,
    COUNT(*) AS trading_days,
    MIN(date) AS first_date,
    MAX(date) AS last_date
FROM tech_stocks
GROUP BY symbol
ORDER BY symbol;
```

### 2. What is the average adjusted close price by year?

```sql
SELECT
    symbol,
    EXTRACT(YEAR FROM date) AS year,
    AVG(close_adjusted) AS avg_adjusted_close
FROM tech_stocks
GROUP BY symbol, year
ORDER BY symbol, year;
```

### 3. Which stocks had the highest single-day trading volume?

```sql
SELECT
    symbol,
    date,
    volume,
    close_adjusted
FROM tech_stocks
ORDER BY volume DESC
LIMIT 20;
```

### 4. What were the largest daily gains and losses?

```sql
WITH daily_returns AS (
    SELECT
        symbol,
        date,
        close_adjusted,
        LAG(close_adjusted) OVER (
            PARTITION BY symbol
            ORDER BY date
        ) AS previous_close
    FROM tech_stocks
)
SELECT
    symbol,
    date,
    close_adjusted,
    previous_close,
    ROUND(
        100 * (close_adjusted - previous_close) / previous_close,
        2
    ) AS daily_return_pct
FROM daily_returns
WHERE previous_close IS NOT NULL
ORDER BY daily_return_pct DESC
LIMIT 20;
```

### 5. What was each stock's yearly return?

```sql
WITH yearly_prices AS (
    SELECT
        symbol,
        EXTRACT(YEAR FROM date) AS year,
        FIRST_VALUE(close_adjusted) OVER (
            PARTITION BY symbol, EXTRACT(YEAR FROM date)
            ORDER BY date
        ) AS first_price,
        FIRST_VALUE(close_adjusted) OVER (
            PARTITION BY symbol, EXTRACT(YEAR FROM date)
            ORDER BY date DESC
        ) AS last_price
    FROM tech_stocks
),
yearly_returns AS (
    SELECT DISTINCT
        symbol,
        year,
        first_price,
        last_price,
        100 * (last_price - first_price) / first_price AS yearly_return_pct
    FROM yearly_prices
)
SELECT
    symbol,
    year,
    ROUND(yearly_return_pct, 2) AS yearly_return_pct
FROM yearly_returns
ORDER BY year, yearly_return_pct DESC;
```

### 6. Which stocks had the strongest full-period return?

```sql
WITH ranked_prices AS (
    SELECT
        symbol,
        date,
        close_adjusted,
        ROW_NUMBER() OVER (
            PARTITION BY symbol
            ORDER BY date
        ) AS first_rank,
        ROW_NUMBER() OVER (
            PARTITION BY symbol
            ORDER BY date DESC
        ) AS last_rank
    FROM tech_stocks
),
start_end AS (
    SELECT
        symbol,
        MAX(CASE WHEN first_rank = 1 THEN close_adjusted END) AS start_price,
        MAX(CASE WHEN last_rank = 1 THEN close_adjusted END) AS end_price
    FROM ranked_prices
    GROUP BY symbol
)
SELECT
    symbol,
    start_price,
    end_price,
    ROUND(100 * (end_price - start_price) / start_price, 2) AS total_return_pct
FROM start_end
ORDER BY total_return_pct DESC;
```

### 7. What is each stock's rolling 30-day volatility?

```sql
WITH returns AS (
    SELECT
        symbol,
        date,
        100 * (
            close_adjusted - LAG(close_adjusted) OVER (
                PARTITION BY symbol
                ORDER BY date
            )
        ) / LAG(close_adjusted) OVER (
            PARTITION BY symbol
            ORDER BY date
        ) AS daily_return_pct
    FROM tech_stocks
)
SELECT
    symbol,
    date,
    daily_return_pct,
    STDDEV(daily_return_pct) OVER (
        PARTITION BY symbol
        ORDER BY date
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) AS rolling_30d_volatility
FROM returns
WHERE daily_return_pct IS NOT NULL
ORDER BY symbol, date;
```

---

## Python Analysis Plan

### Notebook 1: Data Cleaning

Main tasks:

- Load the CSV.
- Drop `Unnamed: 0`.
- Convert `date` to datetime.
- Check missing values.
- Check duplicates.
- Save a cleaned CSV.

Example:

```python
import pandas as pd

df = pd.read_csv("data/raw/tech_stocks.csv")

df = df.drop(columns=["Unnamed: 0"])
df["date"] = pd.to_datetime(df["date"])

df = df.sort_values(["symbol", "date"])

print(df.isna().sum())
print(df.duplicated(["symbol", "date"]).sum())

df.to_csv("data/processed/tech_stocks_clean.csv", index=False)
```

### Notebook 2: SQL Analysis

Main tasks:

- Load the cleaned data into DuckDB.
- Run SQL queries for stock-level performance.
- Export query results to CSV.
- Compare SQL outputs with Python calculations.

Example:

```python
import duckdb

con = duckdb.connect()

con.execute("""
    CREATE TABLE tech_stocks AS
    SELECT *
    FROM read_csv_auto('data/processed/tech_stocks_clean.csv')
""")

query = """
SELECT
    symbol,
    COUNT(*) AS trading_days,
    MIN(date) AS first_date,
    MAX(date) AS last_date
FROM tech_stocks
GROUP BY symbol
ORDER BY symbol;
"""

con.sql(query).df()
```

### Notebook 3: Exploratory Data Analysis

Main tasks:

- Plot adjusted close prices over time.
- Compare cumulative returns.
- Analyze daily return distributions.
- Visualize volume spikes.
- Compare volatility by stock.

Possible charts:

- Adjusted close over time by stock.
- Cumulative return line chart.
- Histogram of daily returns.
- Rolling 30-day volatility chart.
- Risk-return scatterplot.
- Correlation heatmap of daily returns.

### Notebook 4: Feature Engineering

Possible engineered features:

| Feature | Description |
|---|---|
| `daily_return` | Percent change in adjusted close |
| `log_return` | Log difference in adjusted close |
| `return_7d` | 7-day percent return |
| `return_30d` | 30-day percent return |
| `rolling_volatility_30d` | 30-day standard deviation of daily returns |
| `rolling_volume_30d` | 30-day average trading volume |
| `volume_change` | Percent change in volume |
| `price_range_pct` | `(high - low) / open` |
| `target_up_next_day` | 1 if next adjusted close is higher, else 0 |

Example:

```python
import numpy as np

df["daily_return"] = df.groupby("symbol")["close_adjusted"].pct_change()
df["log_return"] = np.log(df["close_adjusted"] / df.groupby("symbol")["close_adjusted"].shift(1))

df["return_7d"] = df.groupby("symbol")["close_adjusted"].pct_change(7)
df["return_30d"] = df.groupby("symbol")["close_adjusted"].pct_change(30)

df["rolling_volatility_30d"] = (
    df.groupby("symbol")["daily_return"]
      .rolling(30)
      .std()
      .reset_index(level=0, drop=True)
)

df["rolling_volume_30d"] = (
    df.groupby("symbol")["volume"]
      .rolling(30)
      .mean()
      .reset_index(level=0, drop=True)
)

df["price_range_pct"] = (df["high"] - df["low"]) / df["open"]

df["target_up_next_day"] = (
    df.groupby("symbol")["close_adjusted"].shift(-1) > df["close_adjusted"]
).astype(int)
```

### Notebook 5: Modeling

A simple modeling task can be added:

> Predict whether a stock's adjusted closing price will increase the next trading day.

This is a classification problem.

Potential models:

- Logistic Regression
- Random Forest
- Gradient Boosting
- XGBoost or LightGBM, optional

Potential features:

- Daily return
- 7-day return
- 30-day return
- Rolling volatility
- Rolling volume
- Price range percentage
- Volume change
- Stock symbol encoded as categorical feature

Potential target:

```text
target_up_next_day
```

Evaluation metrics:

- Accuracy
- Precision
- Recall
- F1-score
- ROC-AUC
- Confusion matrix

Important modeling note:

Stock prediction is noisy. A model that performs only slightly above random can still be meaningful for learning, but the project should avoid overstating predictive power.

---

## Key Metrics

The project will calculate the following metrics.

### Return Metrics

| Metric | Purpose |
|---|---|
| Daily return | Measures day-to-day price movement |
| Cumulative return | Measures total growth over time |
| Annual return | Compares yearly performance |
| Log return | Useful for statistical analysis |

### Risk Metrics

| Metric | Purpose |
|---|---|
| Volatility | Measures variability in returns |
| Rolling volatility | Shows changing risk over time |
| Maximum drawdown | Measures largest peak-to-trough decline |
| Worst daily return | Identifies extreme downside events |

### Trading Activity Metrics

| Metric | Purpose |
|---|---|
| Average volume | Measures typical trading activity |
| Volume spikes | Identifies unusual trading days |
| Rolling volume | Shows changes in market attention |

---

## Possible Final Insights

The final analysis should aim to answer questions like:

- Which stock had the highest cumulative return?
- Which stock had the highest volatility?
- Which stock had the largest drawdown?
- Did higher volatility correspond to higher long-term returns?
- Which years had the strongest and weakest performance?
- Were volume spikes associated with unusually large price movements?
- Did certain stocks become less volatile as they matured?
- How much predictive signal exists in lagged return and volume features?

---

## Installation

Clone the repository:

```bash
git clone https://github.com/your-username/tech-stock-performance-analytics.git
cd tech-stock-performance-analytics
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

Windows:

```bash
.venv\Scripts\activate
```

Mac/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Suggested Requirements

```text
pandas
numpy
matplotlib
seaborn
scikit-learn
duckdb
jupyter
notebook
```

Optional:

```text
plotly
xgboost
lightgbm
```

---

## How to Run the Project

1. Place the raw dataset in:

```text
data/raw/tech_stocks.csv
```

2. Run the cleaning notebook:

```text
notebooks/01_data_cleaning.ipynb
```

3. Run the SQL analysis notebook:

```text
notebooks/02_sql_analysis.ipynb
```

4. Run the EDA notebook:

```text
notebooks/03_exploratory_data_analysis.ipynb
```

5. Run feature engineering:

```text
notebooks/04_feature_engineering.ipynb
```

6. Run modeling:

```text
notebooks/05_modeling.ipynb
```

---

## Deliverables

By the end of the project, this repository should include:

- A cleaned stock price dataset.
- SQL scripts answering core stock performance questions.
- Exploratory charts.
- Engineered financial features.
- A simple predictive model.
- A final summary of findings.
- Clear documentation explaining the workflow.

---

## Project Status

Initial repository setup.

Current stage:

```text
Initial commit: README and project plan
```

Next steps:

- Add raw data to `data/raw/`.
- Create SQL table setup script.
- Create cleaning notebook.
- Begin SQL-based stock performance analysis.

---

## Limitations

This project uses historical stock price data only. It does not include:

- Earnings reports
- Macroeconomic indicators
- Interest rates
- Company fundamentals
- News sentiment
- Analyst ratings
- Real-time market data

Because of this, the project should be interpreted as a historical analytics and learning project rather than a complete investment strategy.

---

## Future Improvements

Possible extensions include:

- Add company metadata for SQL joins.
- Add market index data such as the S&P 500 or NASDAQ Composite.
- Compare each stock against a benchmark.
- Add macroeconomic variables such as interest rates or inflation.
- Add earnings dates and analyze price movement around earnings.
- Build an interactive dashboard.
- Deploy a lightweight Streamlit app.
- Add automated tests for data cleaning and feature engineering.

---

## Notes

This project is for educational and portfolio purposes only. It should not be interpreted as financial advice.
