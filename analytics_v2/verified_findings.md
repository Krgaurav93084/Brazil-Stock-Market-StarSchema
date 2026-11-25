# Verified historical stock analytics
[Successful GitHub Actions run](https://github.com/Krgaurav93084/Brazil-Stock-Market-StarSchema/actions/runs/45622924712), 25 November 2026. Source: [Brazilian Stock Market — Data Warehouse](https://www.kaggle.com/datasets/leomauro/brazilian-stock-market-data-warehouse).
## Data quality
680,150 stock records were loaded; 655,764 passed the analytical quality policy. 24,386 were excluded, including 24,383 non-integral/non-finite/out-of-range volume values under the chosen integer-unit policy. This is a conservative scope restriction, not proof that fractional quantities in the source are erroneous. Four conflicting currency records were separately quarantined. All stock foreign keys reconciled; no duplicate company/date pairs remained. Monthly, yearly and classification-level integer volumes reconciled exactly to 22,521,332,828,182 units.
## Five computed findings
1. 655,764 accepted observations cover 446 company identifiers from 16 March 1998 to 30 December 2020.
2. The largest total volume by source classification was BM&FBOVESPA DIVIDEND INDEX (IDIV): 9,300,845,736,625 units.
3. The largest observed single company-day volume was VALE3: 10,996,395,951 units on 4 August 2020.
4. The highest unweighted mean daily price change among source classifications with at least 20 observations was SPECIAL TAG-ALONG STOCK INDEX (ITAG): 8.236%. This is not an index return; large changes may reflect corporate actions, outliers, missing observations or source issues. Do not annualize it or infer investment performance.
5. Median rolling 20-observation standard deviation of daily price changes was 2.262%.
## Interpretation
The field named sectorCompany in the source contains index classifications; these are not necessarily economic industry sectors. Price returns are not adjusted by this pipeline for splits/dividends. The dataset may mix differing instruments, and aggregate volume is a descriptive reconciliation quantity, not a measure of market capitalization or exchange-wide turnover. Findings are conditional on the accepted records. For production analysis, investigate source definitions for fractional quantities and use adjusted prices and instrument-specific comparisons.
[Generated PNG, quality JSON, findings and sector CSV](https://github.com/Krgaurav93084/Brazil-Stock-Market-StarSchema/actions/runs/45622924712/artifacts/15026451655). Artifact retention applies; workflow can regenerate results.
