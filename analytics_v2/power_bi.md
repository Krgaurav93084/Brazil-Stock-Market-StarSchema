# Historical stock Power BI build
Run load.py and market_kpis.py. Import stock_daily.csv, stock_monthly.csv, stock_yearly.csv and sectors.csv in Power Query. Set date to Date, volume to whole number, returns to decimal. Use each table independently or shared conformed company and period dimensions; never join two facts directly.
Create measures:
```dax
Trading Volume = SUM(stock_daily[volume])
Monthly Trading Volume = SUM(stock_monthly[volume])
Yearly Trading Volume = SUM(stock_yearly[volume])
Monthly Price Return = IF(HASONEVALUE(stock_monthly[keyCompany]) && HASONEVALUE(stock_monthly[month]), SELECTEDVALUE(stock_monthly[period_return]), BLANK())
Yearly Price Return = IF(HASONEVALUE(stock_yearly[keyCompany]) && HASONEVALUE(stock_yearly[year]), SELECTEDVALUE(stock_yearly[period_return]), BLANK())
Average Daily Return = AVERAGE(stock_daily[daily_return])
Rolling Volatility = IF(HASONEVALUE(stock_daily[keyCompany]) && HASONEVALUE(stock_daily[trade_date]),SELECTEDVALUE(stock_daily[volatility_20]),BLANK())
Moving Average 20 = IF(HASONEVALUE(stock_daily[keyCompany]) && HASONEVALUE(stock_daily[trade_date]),SELECTEDVALUE(stock_daily[moving_avg_20]),BLANK())
```
Monthly/yearly price returns are last observed close vs prior contiguous period; not averages or summed daily changes. Company/period guards prevent misleading aggregation. Sector mean return is an unweighted observation average, not a sector index return. Use separate visuals for price, moving averages, volatility, trading volumes and sector comparisons. Native PBIX and screenshot must be created in Power BI Desktop after loading data. Python creates a separate dashboard PNG.
