-- =====================================================================
-- Brazil Stock Market — Star Schema Data Warehouse
-- =====================================================================
-- Two fact tables (factCoins, factStocks) surrounded by three shared /
-- related dimension tables (dimCoin, dimTime, dimCompany), following
-- Kimball's star-schema design (Kimball, 2013).
-- =====================================================================

-- ---------------------------------------------------------------------
-- DIMENSION TABLES
-- ---------------------------------------------------------------------

CREATE TABLE dimCoin (
    keyCoin      INTEGER PRIMARY KEY,
    abbrevCoin   VARCHAR(10)   NOT NULL,   -- e.g. USD, EUR
    nameCoin     VARCHAR(50)   NOT NULL,   -- e.g. DOLAR, EURO
    symbolCoin   VARCHAR(5)
);

CREATE TABLE dimTime (
    keyTime               INTEGER PRIMARY KEY,
    dateTime              DATE          NOT NULL,
    dayTime               SMALLINT,
    dayWeekTime           SMALLINT,
    dayWeekAbbrevTime     VARCHAR(5),
    dayWeekCompleteTime   VARCHAR(15),
    monthTime             SMALLINT,
    monthAbbrevTime       VARCHAR(5),
    monthCompleteTime     VARCHAR(15),
    bimonthTime           SMALLINT,
    quarterTime           SMALLINT,
    semesterTime          SMALLINT,
    yearTime              SMALLINT
);

CREATE TABLE dimCompany (
    keyCompany          INTEGER PRIMARY KEY,
    stockCodeCompany    VARCHAR(10)   NOT NULL,  -- e.g. BRAP4
    nameCompany         VARCHAR(100)  NOT NULL,  -- e.g. BRADESPAR
    sectorCodeCompany   VARCHAR(20),             -- e.g. IMAT
    sectorCompany       VARCHAR(150),
    segmentCompany      VARCHAR(100)
);

-- ---------------------------------------------------------------------
-- FACT TABLES
-- ---------------------------------------------------------------------

-- Fact table 1: currency (coin) value over time
CREATE TABLE factCoins (
    keyTime      INTEGER NOT NULL,
    keyCoin      INTEGER NOT NULL,
    valueCoin    DECIMAL(12,4) NOT NULL,
    PRIMARY KEY (keyTime, keyCoin),
    FOREIGN KEY (keyTime) REFERENCES dimTime(keyTime),
    FOREIGN KEY (keyCoin) REFERENCES dimCoin(keyCoin)
);

-- Fact table 2: stock prices over time, per company
CREATE TABLE factStocks (
    keyTime          INTEGER NOT NULL,
    keyCompany       INTEGER NOT NULL,
    openValueStock   DECIMAL(14,4),
    closeValueStock  DECIMAL(14,4),
    highValueStock   DECIMAL(14,4),
    lowValueStock    DECIMAL(14,4),
    quantityStock    BIGINT,
    PRIMARY KEY (keyTime, keyCompany),
    FOREIGN KEY (keyTime)    REFERENCES dimTime(keyTime),
    FOREIGN KEY (keyCompany) REFERENCES dimCompany(keyCompany)
);

-- ---------------------------------------------------------------------
-- Helpful indexes for the joins used in analysis.sql
-- ---------------------------------------------------------------------
CREATE INDEX idx_factStocks_time    ON factStocks(keyTime);
CREATE INDEX idx_factStocks_company ON factStocks(keyCompany);
CREATE INDEX idx_factCoins_time     ON factCoins(keyTime);
CREATE INDEX idx_factCoins_coin     ON factCoins(keyCoin);
