-- Price and volume summary queries for the tech_stocks table.
-- These summaries use SQLite-compatible aggregate and window functions.

-- 1. Average close price by symbol.
SELECT
    symbol,
    AVG(close) AS avg_close_price
FROM tech_stocks
GROUP BY symbol
ORDER BY symbol;

-- 2. Average volume by symbol.
SELECT
    symbol,
    AVG(volume) AS avg_volume
FROM tech_stocks
GROUP BY symbol
ORDER BY symbol;

-- 3. Highest volume days overall.
SELECT
    symbol,
    date,
    volume,
    close
FROM tech_stocks
ORDER BY volume DESC, symbol, date
LIMIT 20;

-- 4. Highest volume day per symbol using window functions.
WITH ranked_volume AS (
    SELECT
        symbol,
        date,
        volume,
        close,
        ROW_NUMBER() OVER (
            PARTITION BY symbol
            ORDER BY volume DESC, date
        ) AS volume_rank
    FROM tech_stocks
)
SELECT
    symbol,
    date,
    volume,
    close
FROM ranked_volume
WHERE volume_rank = 1
ORDER BY symbol;

-- 5. Average daily price range by symbol, calculated as high - low.
SELECT
    symbol,
    AVG(high - low) AS avg_daily_price_range
FROM tech_stocks
WHERE high IS NOT NULL
  AND low IS NOT NULL
GROUP BY symbol
ORDER BY symbol;

-- 6. Average daily price range percentage by symbol, calculated as (high - low) / close.
SELECT
    symbol,
    AVG((high - low) / close) AS avg_daily_price_range_pct
FROM tech_stocks
WHERE high IS NOT NULL
  AND low IS NOT NULL
  AND close IS NOT NULL
  AND close <> 0
GROUP BY symbol
ORDER BY symbol;
