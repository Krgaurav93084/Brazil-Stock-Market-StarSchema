-- Execute after loading the original schema with historical observations.
DROP VIEW IF EXISTS stock_returns;
CREATE VIEW stock_returns AS
WITH p AS (
 SELECT s.keyCompany,c.stockCodeCompany,c.sectorCompany,t.dateTime AS trade_date,
 s.closeValueStock AS close_price,s.openValueStock AS open_price,s.quantityStock AS volume,
 LAG(s.closeValueStock) OVER(PARTITION BY s.keyCompany ORDER BY t.dateTime) AS previous_close
 FROM factStocks s JOIN dimTime t ON s.keyTime=t.keyTime JOIN dimCompany c ON s.keyCompany=c.keyCompany
)
SELECT *,1.0*(close_price-previous_close)/NULLIF(previous_close,0) AS daily_return,
 1.0*(close_price-open_price)/NULLIF(open_price,0) AS intraday_return,
 AVG(close_price) OVER(PARTITION BY keyCompany ORDER BY trade_date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS moving_avg_20
FROM p;
-- Monthly volume and average observed daily returns; not compounded monthly returns.
SELECT sectorCompany,substr(CAST(trade_date AS VARCHAR(20)),1,7) AS month,
 SUM(volume) AS traded_volume,AVG(daily_return) AS mean_daily_return,COUNT(daily_return) AS observations
FROM stock_returns GROUP BY sectorCompany,substr(CAST(trade_date AS VARCHAR(20)),1,7);
-- Price integrity exceptions
SELECT * FROM factStocks WHERE openValueStock<=0 OR closeValueStock<=0 OR quantityStock<0
 OR highValueStock<lowValueStock OR highValueStock<openValueStock OR highValueStock<closeValueStock
 OR lowValueStock>openValueStock OR lowValueStock>closeValueStock
 OR openValueStock IS NULL OR closeValueStock IS NULL;
