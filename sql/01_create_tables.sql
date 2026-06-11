DROP TABLE IF EXISTS tech_stocks;

CREATE TABLE tech_stocks (
    date TEXT NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume INTEGER,
    symbol TEXT NOT NULL,
    trading_year INTEGER,
    trading_month TEXT,
    PRIMARY KEY (symbol, date)
);
