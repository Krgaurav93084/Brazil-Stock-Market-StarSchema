# Brazilian market | Validated historical observations

Power BI Project (PBIP) source: editable semantic model, report page with native visual definitions, M query, DAX measures and expected-value test query. This is not a PBIX binary or a screenshot. Desktop runtime compatibility has not yet been tested.

Data: [verified_kpis.csv](../../analytics_v2/verified_kpis.csv) from previously validated repository results. This report uses the verified aggregate KPI snapshot; it is not an order- or stock-observation-level drill-down model. The separate warehouse and pipeline remain in the parent repository.

1. Clone/download the entire repository; keep the report and semantic-model folders beside the PBIP.
2. Use current Power BI Desktop on Windows. If needed enable Power BI project/PBIR support in Options > Preview features, restart, and open StockMarket.pbip.
3. Refresh the model. Select anonymous credentials for the public raw.githubusercontent.com source if prompted. Check the Power Query preview and query errors.
4. Open DAX Query View, paste verify.dax, run and compare all measures with expected_results.csv (allow normal floating-point rounding). Do not sum mixed-unit snapshot values.
5. Inspect all visuals. Save As > Power BI Desktop file (*.pbix). Capture genuine report screenshots after successful refresh and upload the PBIX and screenshots to GitHub (override the gitignore intentionally or use Git LFS where necessary).

References: https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview and https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report . No Power BI Desktop runtime, PBIX export or screenshot was executed during creation.
