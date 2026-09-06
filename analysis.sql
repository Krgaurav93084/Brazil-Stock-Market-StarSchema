-- =====================================================================
-- Brazil Stock Market — Analysis Queries
-- Recreates the joins / calculated column / pivot table steps described
-- in the "Data Modeling" and "Analysis & Evaluation" sections of the
-- project deck.
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1) Join factStocks + dimTime + dimCompany
--    ("We combined the tables factStocks... and dimTime using the
--    'keyTime' column and with dimCompany using 'keyCompany'")
-- ---------------------------------------------------------------------
CREATE VIEW vw_stock_detail AS
SELECT
    t.keyTime,
    t.dateTime,
    t.dayWeekCompleteTime,
    t.monthCompleteTime,
    t.quarterTime,
    t.semesterTime,
    t.yearTime,
    c.keyCompany,
    c.stockCodeCompany,
    c.nameCompany,
    c.sectorCodeCompany,
    c.sectorCompany,
    c.segmentCompany,
    s.openValueStock,
    s.closeValueStock,
    s.highValueStock,
    s.lowValueStock,
    s.quantityStock
FROM factStocks s
JOIN dimTime    t ON s.keyTime    = t.keyTime
JOIN dimCompany c ON s.keyCompany = c.keyCompany;

-- ---------------------------------------------------------------------
-- 2) Join factCoins + dimTime + dimCoin (currency exchange analysis)
-- ---------------------------------------------------------------------
CREATE VIEW vw_coin_detail AS
SELECT
    t.keyTime,
    t.dateTime,
    dc.abbrevCoin,
    dc.nameCoin,
    dc.symbolCoin,
    fc.valueCoin
FROM factCoins fc
JOIN dimTime t ON fc.keyTime = t.keyTime
JOIN dimCoin dc ON fc.keyCoin = dc.keyCoin;

-- ---------------------------------------------------------------------
-- 3) Creation of a new column: daily percentage change in stock price
--    percent_change = ((close - open) / open) * 100
-- ---------------------------------------------------------------------
CREATE VIEW vw_stock_daily_pct_change AS
SELECT
    v.*,
    ROUND(((v.closeValueStock - v.openValueStock) / NULLIF(v.openValueStock, 0)) * 100, 4)
        AS daily_percentage_change
FROM vw_stock_detail v;

-- ---------------------------------------------------------------------
-- 4) Pivot-style aggregation: average daily percentage change by sector
--    ("Aggregated the daily percentage change data by sector to
--    calculate the average performance of each sector over time")
-- ---------------------------------------------------------------------
SELECT
    sectorCompany,
    ROUND(AVG(daily_percentage_change), 2) AS avg_daily_percentage_change
FROM vw_stock_daily_pct_change
GROUP BY sectorCompany
ORDER BY avg_daily_percentage_change DESC;

-- ---------------------------------------------------------------------
-- 5) Business question: opening/closing/high/low values of a stock on a
--    given day
-- ---------------------------------------------------------------------
SELECT
    dateTime, stockCodeCompany, nameCompany,
    openValueStock, closeValueStock, highValueStock, lowValueStock
FROM vw_stock_detail
WHERE dateTime = DATE '2012-05-01'
ORDER BY nameCompany;

-- ---------------------------------------------------------------------
-- 6) Business question: which days of the week had the highest trading
--    volume?
-- ---------------------------------------------------------------------
SELECT
    dayWeekCompleteTime,
    SUM(quantityStock) AS total_volume
FROM vw_stock_detail
GROUP BY dayWeekCompleteTime
ORDER BY total_volume DESC;

-- ---------------------------------------------------------------------
-- 7) Business question: top companies by high stock value
-- ---------------------------------------------------------------------
SELECT
    nameCompany,
    MAX(highValueStock) AS max_high_value
FROM vw_stock_detail
GROUP BY nameCompany
ORDER BY max_high_value DESC
LIMIT 10;
