-- Company metadata join queries for the tech_stocks and company_metadata tables.
-- Run after loading data/processed/tech_stocks_clean.csv and, when available,
-- data/raw/company_metadata.csv into SQLite.

-- 1. Join tech_stocks to company_metadata.
SELECT
    s.date,
    s.symbol,
    m.company_name,
    m.sector,
    m.industry,
    m.exchange,
    m.founded_year,
    m.headquarters,
    s.open,
    s.high,
    s.low,
    s.close,
    s.volume,
    s.trading_year,
    s.trading_month
FROM tech_stocks AS s
LEFT JOIN company_metadata AS m
    ON s.symbol = m.symbol
ORDER BY s.symbol, s.date;

-- 2. Average close and volume by company_name.
SELECT
    COALESCE(m.company_name, s.symbol) AS company_name,
    AVG(s.close) AS avg_close_price,
    AVG(s.volume) AS avg_volume
FROM tech_stocks AS s
LEFT JOIN company_metadata AS m
    ON s.symbol = m.symbol
GROUP BY COALESCE(m.company_name, s.symbol)
ORDER BY company_name;

-- 3. Average volume by industry.
SELECT
    COALESCE(m.industry, 'Unknown') AS industry,
    AVG(s.volume) AS avg_volume
FROM tech_stocks AS s
LEFT JOIN company_metadata AS m
    ON s.symbol = m.symbol
GROUP BY COALESCE(m.industry, 'Unknown')
ORDER BY industry;

-- 4. Trading date range by company.
SELECT
    COALESCE(m.company_name, s.symbol) AS company_name,
    MIN(s.date) AS first_trading_date,
    MAX(s.date) AS last_trading_date,
    COUNT(*) AS trading_day_count
FROM tech_stocks AS s
LEFT JOIN company_metadata AS m
    ON s.symbol = m.symbol
GROUP BY COALESCE(m.company_name, s.symbol)
ORDER BY company_name;

-- 5. Highest average daily price range percentage by company.
SELECT
    COALESCE(m.company_name, s.symbol) AS company_name,
    AVG((s.high - s.low) / s.close) AS avg_daily_price_range_pct
FROM tech_stocks AS s
LEFT JOIN company_metadata AS m
    ON s.symbol = m.symbol
WHERE s.high IS NOT NULL
  AND s.low IS NOT NULL
  AND s.close IS NOT NULL
  AND s.close <> 0
GROUP BY COALESCE(m.company_name, s.symbol)
ORDER BY avg_daily_price_range_pct DESC, company_name;
