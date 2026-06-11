DROP TABLE IF EXISTS tech_stocks;
DROP TABLE IF EXISTS company_metadata;

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


CREATE TABLE company_metadata (
    symbol TEXT PRIMARY KEY,
    company_name TEXT,
    sector TEXT,
    industry TEXT,
    exchange TEXT,
    founded_year INTEGER,
    headquarters TEXT
);
