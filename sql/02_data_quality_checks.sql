-- Data quality checks for the tech_stocks table.
-- Run after loading data/processed/tech_stocks_clean.csv into SQLite.

-- 1. Total row count.
SELECT
    COUNT(*) AS total_rows
FROM tech_stocks;

-- 2. Unique symbol count.
SELECT
    COUNT(DISTINCT symbol) AS unique_symbol_count
FROM tech_stocks;

-- 3. Min and max date by symbol.
SELECT
    symbol,
    MIN(date) AS min_date,
    MAX(date) AS max_date
FROM tech_stocks
GROUP BY symbol
ORDER BY symbol;

-- 4. Duplicate symbol-date check.
SELECT
    symbol,
    date,
    COUNT(*) AS duplicate_count
FROM tech_stocks
GROUP BY symbol, date
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC, symbol, date;

-- 5. Missing close price check.
SELECT
    symbol,
    date,
    close
FROM tech_stocks
WHERE close IS NULL
ORDER BY symbol, date;

-- 6. Trading day count by symbol.
SELECT
    symbol,
    COUNT(*) AS trading_day_count
FROM tech_stocks
GROUP BY symbol
ORDER BY symbol;
