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
            # Source releases can differ in optional descriptive calendar fields.
            # Normalize case/whitespace, preserve identifiers, derive calendar attributes from actual dates.
            normalized={str(x).strip().lower():x for x in df.columns}
            df=df.rename(columns={normalized[x.lower()]:x for x in columns if x.lower() in normalized})
            print(name,"source headers",list(df.columns),flush=True)
            if name=="dimTime":
                if not {"keyTime","dateTime"}.issubset(df.columns):
                    raise ValueError(f"Missing required calendar key/date; source headers: {list(df.columns)}")
                dt=pd.to_datetime(df.dateTime,errors="raise")
                derived={"dayTime":dt.dt.day,"dayWeekTime":dt.dt.dayofweek+1,
                    "dayWeekAbbrevTime":dt.dt.day_name().str[:3],"dayWeekCompleteTime":dt.dt.day_name(),
                    "monthTime":dt.dt.month,"monthAbbrevTime":dt.dt.month_name().str[:3],
                    "monthCompleteTime":dt.dt.month_name(),"bimonthTime":(dt.dt.month-1)//2+1,
                    "quarterTime":dt.dt.quarter,"semesterTime":(dt.dt.month-1)//6+1,"yearTime":dt.dt.year}
                for col,value in derived.items():
                    if col not in df.columns:df[col]=value
                df["dateTime"]=dt.dt.strftime("%Y-%m-%d")
            required={"dimCoin":{"keyCoin","abbrevCoin","nameCoin"},
                      "dimTime":{"keyTime","dateTime"},
                      "dimCompany":{"keyCompany","stockCodeCompany","nameCompany","sectorCompany"},
                      "factCoins":{"keyTime","keyCoin","valueCoin"},
                      "factStocks":set(columns)}[name]
            missing=required-set(df.columns)
            if missing:raise ValueError(f"{name}: required columns missing {missing}; source headers: {list(df.columns)}")
            for col in columns:
                if col not in df.columns:df[col]=None
            df=df[columns].copy()
            # Remove exact duplicates; quarantine every conflicting key rather than inventing a value.
            raw_count=len(df)
            df=df.drop_duplicates().copy()
            exact_duplicates=raw_count-len(df)
            keys={"dimCoin":["keyCoin"],"dimTime":["keyTime"],"dimCompany":["keyCompany"],
                  "factCoins":["keyTime","keyCoin"],"factStocks":["keyTime","keyCompany"]}[name]
            conflicts=df.duplicated(subset=keys,keep=False)
            conflict_count=int(conflicts.sum())
            if conflict_count:
                if not name.startswith("fact"):
                    raise ValueError(f"{name}: {conflict_count} conflicting dimension rows")
                quarantine=db.parent/"quarantine"
                quarantine.mkdir(parents=True,exist_ok=True)
                df.loc[conflicts].to_csv(quarantine/(name+"_conflicting_keys.csv"),index=False)
                df=df.loc[~conflicts].copy()
            print(json.dumps({"table":name,"source_rows":raw_count,"exact_duplicates_removed":exact_duplicates,"conflicting_rows_quarantined":conflict_count,"loaded_rows":len(df)}),flush=True)
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
