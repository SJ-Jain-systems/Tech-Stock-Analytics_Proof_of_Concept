-- Return analysis queries for the tech_stocks table.
-- Returns are calculated from close prices using SQLite window functions.

-- 1. Daily return by symbol using LAG(close).
WITH daily_prices AS (
    SELECT
        symbol,
        date,
        close,
        LAG(close) OVER (
            PARTITION BY symbol
            ORDER BY date
        ) AS previous_close
    FROM tech_stocks
)
SELECT
    symbol,
    date,
    close,
    previous_close,
    (close - previous_close) / previous_close AS daily_return
FROM daily_prices
WHERE previous_close IS NOT NULL
  AND previous_close <> 0
ORDER BY symbol, date;

-- 2. Average daily return by symbol.
WITH daily_returns AS (
    SELECT
        symbol,
        date,
        close,
        LAG(close) OVER (
            PARTITION BY symbol
            ORDER BY date
        ) AS previous_close
    FROM tech_stocks
)
SELECT
    symbol,
    AVG((close - previous_close) / previous_close) AS avg_daily_return
FROM daily_returns
WHERE previous_close IS NOT NULL
  AND previous_close <> 0
GROUP BY symbol
ORDER BY symbol;

-- 3. Best single-day return by symbol.
WITH daily_returns AS (
    SELECT
        symbol,
        date,
        close,
        LAG(close) OVER (
            PARTITION BY symbol
            ORDER BY date
        ) AS previous_close
    FROM tech_stocks
),
ranked_returns AS (
    SELECT
        symbol,
        date,
        close,
        previous_close,
        (close - previous_close) / previous_close AS daily_return,
        ROW_NUMBER() OVER (
            PARTITION BY symbol
            ORDER BY (close - previous_close) / previous_close DESC, date
        ) AS return_rank
    FROM daily_returns
    WHERE previous_close IS NOT NULL
      AND previous_close <> 0
)
SELECT
    symbol,
    date,
    close,
    previous_close,
    daily_return
FROM ranked_returns
WHERE return_rank = 1
ORDER BY symbol;

-- 4. Worst single-day return by symbol.
WITH daily_returns AS (
    SELECT
        symbol,
        date,
        close,
        LAG(close) OVER (
            PARTITION BY symbol
            ORDER BY date
        ) AS previous_close
    FROM tech_stocks
),
ranked_returns AS (
    SELECT
        symbol,
        date,
        close,
        previous_close,
        (close - previous_close) / previous_close AS daily_return,
        ROW_NUMBER() OVER (
            PARTITION BY symbol
            ORDER BY (close - previous_close) / previous_close ASC, date
        ) AS return_rank
    FROM daily_returns
    WHERE previous_close IS NOT NULL
      AND previous_close <> 0
)
SELECT
    symbol,
    date,
    close,
    previous_close,
    daily_return
FROM ranked_returns
WHERE return_rank = 1
ORDER BY symbol;

-- 5. Monthly return by symbol using first and last close of each month.
WITH monthly_prices AS (
    SELECT
        symbol,
        strftime('%Y-%m', date) AS trading_month,
        date,
        close,
        ROW_NUMBER() OVER (
            PARTITION BY symbol, strftime('%Y-%m', date)
            ORDER BY date
        ) AS first_day_rank,
        ROW_NUMBER() OVER (
            PARTITION BY symbol, strftime('%Y-%m', date)
            ORDER BY date DESC
        ) AS last_day_rank
    FROM tech_stocks
),
monthly_closes AS (
    SELECT
        symbol,
        trading_month,
        MAX(CASE WHEN first_day_rank = 1 THEN date END) AS first_trading_date,
        MAX(CASE WHEN first_day_rank = 1 THEN close END) AS first_close,
        MAX(CASE WHEN last_day_rank = 1 THEN date END) AS last_trading_date,
        MAX(CASE WHEN last_day_rank = 1 THEN close END) AS last_close
    FROM monthly_prices
    GROUP BY symbol, trading_month
)
SELECT
    symbol,
    trading_month,
    first_trading_date,
    last_trading_date,
    first_close,
    last_close,
    (last_close - first_close) / first_close AS monthly_return
FROM monthly_closes
WHERE first_close IS NOT NULL
  AND first_close <> 0
ORDER BY symbol, trading_month;

-- 6. Yearly return by symbol.
WITH yearly_prices AS (
    SELECT
        symbol,
        strftime('%Y', date) AS trading_year,
        date,
        close,
        ROW_NUMBER() OVER (
            PARTITION BY symbol, strftime('%Y', date)
            ORDER BY date
        ) AS first_day_rank,
        ROW_NUMBER() OVER (
            PARTITION BY symbol, strftime('%Y', date)
            ORDER BY date DESC
        ) AS last_day_rank
    FROM tech_stocks
),
yearly_closes AS (
    SELECT
        symbol,
        trading_year,
        MAX(CASE WHEN first_day_rank = 1 THEN date END) AS first_trading_date,
        MAX(CASE WHEN first_day_rank = 1 THEN close END) AS first_close,
        MAX(CASE WHEN last_day_rank = 1 THEN date END) AS last_trading_date,
        MAX(CASE WHEN last_day_rank = 1 THEN close END) AS last_close
    FROM yearly_prices
    GROUP BY symbol, trading_year
)
SELECT
    symbol,
    trading_year,
    first_trading_date,
    last_trading_date,
    first_close,
    last_close,
    (last_close - first_close) / first_close AS yearly_return
FROM yearly_closes
WHERE first_close IS NOT NULL
  AND first_close <> 0
ORDER BY symbol, trading_year;
