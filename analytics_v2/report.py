"""Analyze a populated SQLite warehouse using the original schema."""
import argparse
from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def run(db,output):
    output.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(db) as conn:
        conn.executescript((Path(__file__).parent/"advanced.sql").read_text().split("-- Monthly volume")[0])
        df=pd.read_sql_query("SELECT * FROM stock_returns ORDER BY keyCompany,trade_date",conn,parse_dates=["trade_date"])
    if df.empty:
        raise ValueError("Load the original historical data before running.")
    df["daily_return"]=pd.to_numeric(df.daily_return,errors="coerce").replace([np.inf,-np.inf],np.nan)
    df["rolling_volatility_20"]=df.groupby("keyCompany").daily_return.transform(lambda s:s.rolling(20,min_periods=20).std())
    df["month"]=df.trade_date.dt.to_period("M").astype(str)
    summary=df.groupby(["sectorCompany","month"],dropna=False).agg(mean_daily_return=("daily_return","mean"),volume=("volume","sum"),observations=("daily_return","count")).reset_index()
    df.to_csv(output/"stock_returns.csv",index=False)
    summary.to_csv(output/"sector_summary.csv",index=False)
    fig,ax=plt.subplots(figsize=(11,5))
    for sector,g in summary.groupby("sectorCompany"):
        ax.plot(pd.to_datetime(g.month),g.mean_daily_return*100,label=sector)
    ax.set_ylabel("Mean daily return (%)")
    ax.set_title("Historical sector comparison (unweighted observations)")
    ax.legend(fontsize=7);fig.tight_layout();fig.savefig(output/"sector_dashboard.png",dpi=140);plt.close(fig)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("db",type=Path)
    p.add_argument("--output",type=Path,default=Path("output"))
    a=p.parse_args()
    if not a.db.is_file():p.error("Existing database required")
    run(a.db,a.output)
