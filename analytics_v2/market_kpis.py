"""Actual findings and BI-ready tables from the populated historical warehouse."""
from pathlib import Path
import argparse,sqlite3,json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def run(db,out):
    out.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(db) as c:
        counts={t:c.execute("SELECT COUNT(*) FROM "+t).fetchone()[0] for t in ["dimTime","dimCoin","dimCompany","factStocks","factCoins"]}
        d=pd.read_sql_query("""SELECT s.keyCompany,c.stockCodeCompany,c.sectorCompany,t.dateTime trade_date,
        s.openValueStock open_price,s.closeValueStock close_price,s.highValueStock high_price,
        s.lowValueStock low_price,s.quantityStock volume FROM factStocks s JOIN dimCompany c USING(keyCompany) JOIN dimTime t USING(keyTime)
        ORDER BY s.keyCompany,t.dateTime""",c,parse_dates=["trade_date"])
        fk=len(c.execute("PRAGMA foreign_key_check").fetchall())
    if d.empty: raise ValueError("No matched stock observations")
    duplicate=d.duplicated(["keyCompany","trade_date"])
    numeric=["open_price","close_price","high_price","low_price","volume"]
    for col in numeric:d[col]=pd.to_numeric(d[col],errors="coerce")
    bad=(d[numeric].isna().any(axis=1)|d.trade_date.isna()|(d[["open_price","close_price","high_price","low_price"]]<=0).any(axis=1)|(d.volume<0)|(d.high_price<d[["open_price","close_price","low_price"]].max(axis=1))|(d.low_price>d[["open_price","close_price"]].min(axis=1)))
    # Trading quantity is an integer count of units, not floating-point money.
    # Exclude non-integral/non-finite or out-of-range source values explicitly.
    quantity=d.volume
    fractional_or_invalid_volume=(quantity.notna() & (~np.isfinite(quantity) | (quantity % 1 != 0) | (quantity >= 2**63)))
    bad=bad | fractional_or_invalid_volume
    quality={"fractional_or_invalid_volume_rows":int(fractional_or_invalid_volume.sum()),"table_counts":counts,"foreign_key_violations":fk,"matched_rows":len(d),"unmatched_stock_rows":counts["factStocks"]-len(d),"duplicate_company_date":int(duplicate.sum()),"invalid_rows":int(bad.sum()),"accepted_rows":int((~(bad|duplicate)).sum())}
    d.loc[bad|duplicate].to_csv(out/"rejected.csv",index=False)
    d=d.loc[~(bad|duplicate)].copy()
    if d.empty:raise ValueError("No valid stock observations")
    d["volume"]=d.volume.astype("int64")
    exact_total=sum(int(x) for x in d.volume)
    if exact_total>np.iinfo(np.int64).max:
        raise OverflowError("Trading volume exceeds signed 64-bit aggregation range")
    quality["accepted_volume_units"]=exact_total
    d["sectorCompany"]=d.sectorCompany.fillna("Unknown")
    g=d.groupby("keyCompany")
    d["daily_return"]=g.close_price.pct_change(fill_method=None)
    d["moving_avg_20"]=g.close_price.transform(lambda s:s.rolling(20,min_periods=20).mean())
    d["volatility_20"]=d.groupby("keyCompany").daily_return.transform(lambda s:s.rolling(20,min_periods=20).std())
    d["month"]=d.trade_date.dt.to_period("M").astype(str)
    d["year"]=d.trade_date.dt.year
    def period_table(period):
        a=d.groupby(["keyCompany","stockCodeCompany",period],as_index=False).agg(period_close=("close_price","last"),volume=("volume","sum"),observations=("close_price","count"))
        a=a.sort_values(["keyCompany",period])
        # Compare with prior period only if it is contiguous.
        periods=pd.PeriodIndex(a[period].astype(str),freq="M" if period=="month" else "Y").asi8
        a["period_index"]=periods
        a["period_return"]=a.groupby("keyCompany").period_close.pct_change(fill_method=None).where(a.groupby("keyCompany").period_index.diff()==1)
        return a.drop(columns="period_index")
    monthly,yearly=period_table("month"),period_table("year")
    sectors=d.groupby("sectorCompany").agg(volume=("volume","sum"),mean_daily_return=("daily_return","mean"),observations=("daily_return","count")).reset_index()
    for label,frame in [("monthly",monthly),("yearly",yearly),("sector",sectors)]:
        actual=sum(int(x) for x in frame.volume)
        assert actual==exact_total,(label,actual,exact_total)
    d.to_csv(out/"stock_daily.csv",index=False);monthly.to_csv(out/"stock_monthly.csv",index=False);yearly.to_csv(out/"stock_yearly.csv",index=False);sectors.to_csv(out/"sectors.csv",index=False)
    (out/"quality.json").write_text(json.dumps(quality,indent=2))
    top=sectors.loc[sectors.volume.idxmax()]
    eligible=sectors[sectors.observations>=20]
    best=eligible.loc[eligible.mean_daily_return.idxmax()] if len(eligible) else None
    peak=d.loc[d.volume.idxmax()]
    vol=d.dropna(subset=["volatility_20"])
    lines=["# Calculated historical findings","Unadjusted price observations; no investment recommendations.",
    f"1. Accepted {len(d):,} stock observations across {d.keyCompany.nunique():,} companies from {d.trade_date.min():%Y-%m-%d} to {d.trade_date.max():%Y-%m-%d}.",
    f"2. Highest total observed trading volume sector: {top.sectorCompany}, {top.volume:,.0f} units.",
    f"3. Highest single company-day volume: {peak.stockCodeCompany}, {peak.volume:,.0f} on {peak.trade_date:%Y-%m-%d}.",
    f"4. Highest mean observed daily return among sectors with >=20 return observations: {best.sectorCompany}, {best.mean_daily_return:.3%}." if best is not None else "4. Insufficient observations for sector return comparison.",
    f"5. Median rolling 20-observation daily return volatility: {vol.volatility_20.median():.3%}." if len(vol) else "5. Insufficient observations for rolling volatility."]
    (out/"findings.md").write_text("\n\n".join(lines))
    fig,ax=plt.subplots(2,2,figsize=(12,8),layout="constrained")
    d.groupby("trade_date").volume.sum().plot(ax=ax[0,0],title="Daily observed trading volume")
    sectors.nlargest(10,"volume").set_index("sectorCompany").volume.plot.barh(ax=ax[0,1],title="Sector volume")
    if len(eligible):eligible.nlargest(10,"mean_daily_return").set_index("sectorCompany").mean_daily_return.mul(100).plot.barh(ax=ax[1,0],title="Mean observed return (%)")
    if len(vol):vol.groupby("trade_date").volatility_20.median().mul(100).plot(ax=ax[1,1],title="Median rolling volatility (%)")
    fig.savefig(out/"dashboard.png",dpi=150);plt.close(fig)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("db",type=Path);p.add_argument("--output",type=Path,default=Path("output"));a=p.parse_args()
    if not a.db.is_file():p.error("Load the historical database first")
    run(a.db,a.output)
