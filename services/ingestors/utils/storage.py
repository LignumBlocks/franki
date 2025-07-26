import pandas as pd
import pathlib

BASE = pathlib.Path("/data/parquet")

def dump_parquet(df: pd.DataFrame, source: str):
    ts = pd.to_datetime(df["timestamp"].iloc[-1], unit="ms", utc=True)
    path = BASE / source / f"{ts.date()}.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        old = pd.read_parquet(path)
        df = pd.concat([old, df], ignore_index=True)

    df.to_parquet(path, index=False)
