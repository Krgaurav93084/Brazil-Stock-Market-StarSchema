# Tableau | Brazil Stock Market Analytics
Mac-compatible Tableau Desktop Professional or Public Edition authoring kit. This folder contains instructions and a workflow that packages previously validated historical outputs. It is not a completed Tableau workbook or a Tableau runtime test.

[Historical validation](https://github.com/Krgaurav93084/Brazil-Stock-Market-StarSchema/actions/runs/45622924712) · [Tableau data-kit workflow](https://github.com/Krgaurav93084/Brazil-Stock-Market-StarSchema/actions/workflows/tableau-data-kit.yml)

## Build the Tableau dashboard
Use verified_kpis.csv and sectors.csv as separate data sources. The packaged data is an aggregate snapshot, not a full stock-day dataset.
| Sheet | Data | Columns | Rows / Marks |
|---|---|---|---|
| Source stock records | verified_kpis.csv | none | calculated Source Records, Text |
| Accepted observations | verified_kpis.csv | none | calculated Accepted Records, Text |
| Accepted rate | verified_kpis.csv | none | calculated Accepted Rate, Text |
| Company identifiers | verified_kpis.csv | none | calculated Companies, Text |
| Volume by source classification | sectors.csv | SUM(volume) | sectorCompany, Bar |
| Mean price change by classification | sectors.csv | AVG(mean_daily_return) | sectorCompany, Bar, filter observations >= 20 |

### Calculated fields (verified KPI snapshot source)
- Source Records: `MAX(IF [metric] = "Source stock records" THEN [value] END)`
- Accepted Records: `MAX(IF [metric] = "Accepted stock records" THEN [value] END)`
- Accepted Rate: `[Accepted Records] / [Source Records]`
- Companies: `MAX(IF [metric] = "Company identifiers" THEN [value] END)`
- Median Volatility: `MAX(IF [metric] = "Median rolling volatility" THEN [value] END)`
Format rates as percentages. Expected values: 680,150 loaded; 655,764 accepted; 446 company identifiers; approximately 96.41% acceptance; 2.262% median rolling volatility. 24,386 rows excluded under the documented quality policy, including 24,383 integer-volume-policy exclusions.
Use the full historical pipeline output stock_daily.csv and stock_monthly.csv after regenerating locally for additional date filters and trend charts. Source classifications may be indices rather than industries; unadjusted prices and missing observations limit interpretation. Do not interpret the mean as an investment return.

## Open and publish on a Mac
1. Download the Tableau data-kit ZIP from the latest successful workflow and extract it.
2. In Tableau Desktop, Connect > Text File and select the required CSVs. Verify column types and calculations; create the worksheets and dashboard described above.
3. Compare displayed values with the validated findings in the repository. Save a packaged workbook (.twbx) using File > Save As.
4. For a public portfolio, use Server > Tableau Public > Save to Tableau Public with your own authenticated Tableau account. Use only public, non-confidential data and respect the original dataset license. Save an actual image of the rendered dashboard and upload the workbook, screenshot and public link to GitHub.
5. Record Tableau version, tested metrics, and any differences.

The existing Power BI project remains separate. Tableau calculations do not execute DAX or Power Query. This kit has not been opened in Tableau; no workbook, screenshot or public Tableau link is claimed.
