"""Load original CSV tables after mapping their headers to schema.sql."""
from pathlib import Path
import argparse, sqlite3, json
import pandas as pd
ROOT=Path(__file__).resolve().parent
TABLES=["dimCoin","dimTime","dimCompany","factCoins","factStocks"]
def main(data,db):
    if db.exists(): raise FileExistsError("Choose a new database path to preserve existing data")
    frames={}
    for name in TABLES:
        path=data/(name+".csv")
        frames[name]=pd.read_csv(path)
    with sqlite3.connect(":memory:") as c:
        c.execute("PRAGMA foreign_keys=ON")
        c.executescript((ROOT.parent/"schema.sql").read_text())
        counts={}
        for name,df in frames.items():
            columns=[x[1] for x in c.execute("PRAGMA table_info("+name+")")]
            if not set(columns).issubset(df.columns): raise ValueError(f"{name}: map headers to {columns}")
            df=df[columns].copy()
            if name=="dimTime": df["dateTime"]=pd.to_datetime(df.dateTime,errors="raise").dt.strftime("%Y-%m-%d")
            # Use executemany to retain schema constraints, rather than replacing tables.
            vals=df.astype(object).where(df.notna(),None)
            c.executemany("INSERT INTO "+name+" VALUES ("+",".join("?" for _ in columns)+")",vals.itertuples(index=False,name=None))
            counts[name]=len(df)
        assert not c.execute("PRAGMA foreign_key_check").fetchall()
        c.commit()
        with sqlite3.connect(db) as dst: c.backup(dst)
    print(json.dumps(counts,indent=2))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("data",type=Path);p.add_argument("db",type=Path);a=p.parse_args();main(a.data,a.db)
