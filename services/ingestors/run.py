# services/ingestors/run.py
import os, time, subprocess, sys, yaml
import pandas as pd
from pathlib import Path

HL_START = os.getenv("HL_START", "2024-01-01")    # yyyy-mm-dd
HL_LOOP_MIN = int(os.getenv("HL_LOOP_MINUTES", "360"))
TF_LIST = os.getenv("HL_TIMEFRAMES", "1m,5m,15m,1h").split(",")
DST_PARQUET = Path(os.getenv("HL_STORAGE_PARQUET", "/data/parquet"))
DST_FEATHER = Path(os.getenv("HL_STORAGE_FEATHER", "/freqtrade/user_data/data/hyperliquid/futures"))
PAIRS_FILE = Path("/app/pairs.yaml")

CLI = "python /opt/hyperliquid-historical/hyperliquid-historical.py"

TF_MAP = {"1m":"1min","5m":"5min","15m":"15min","1h":"1h"}

def yyyymmdd(dt: str) -> str:
    # "2024-01-01" -> "20240101"
    return dt.replace("-", "")

def tf_to_rule(tf):
    return TF_MAP[tf]

def run_cli(action: str, assets: list[str], sd: str, ed: str):
    cmd = " ".join([CLI, action, "-sd", sd, "-ed", ed] + assets)
    print(f"[INGESTOR] Ejecutando: {cmd}", flush=True)
    subprocess.run(cmd, shell=True, check=True)

def export_feather(df_ohlcv: pd.DataFrame, ft_pair: str, tf: str):
    DST_FEATHER.mkdir(parents=True, exist_ok=True)
    out = DST_FEATHER / f"{ft_pair}-{tf}-futures.feather"
    tmp = out.with_suffix(".feather.tmp")
    ft = df_ohlcv.reset_index().rename(columns={"timestamp":"date"})
    ft["date"] = (ft["date"].astype("int64") // 10**6)  # epoch ms UTC
    ft = ft[["date","open","high","low","close","volume"]].dropna()
    ft.to_feather(tmp)
    os.replace(tmp, out)

def ohlcv_from_csv_dir(csv_dir: Path) -> pd.DataFrame:
    # Une todos los CSV producidos por "to_csv"
    # Formato esperado (repo): date_time, timestamp, level, price, size, number
    # Usaremos "level==1" como top-of-book para aproximar precio, y agregamos volumen.
    files = sorted(csv_dir.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"Sin CSV en {csv_dir}")
    df = pd.concat((pd.read_csv(f) for f in files), ignore_index=True)
    # timestamp puede venir en ms/s; normalizamos
    unit = "ms" if df["timestamp"].astype(str).str.len().median() >= 13 else "s"
    ts = pd.to_datetime(df["timestamp"], unit=unit, utc=True)
    df = df.assign(timestamp=ts)
    # Filtra level 1 para precio; suma size como proxy de volumen
    top = df[df["level"] == 1] if df["level"].dtype != object else df[df["level"].astype(str) == "1"]
    # Si level es string, normaliza:
    top = top.copy()
    top["price"] = pd.to_numeric(top["price"], errors="coerce")
    top["size"]  = pd.to_numeric(top["size"],  errors="coerce").fillna(0)

    # Re-sample a OHLCV
    ohlcv_1m = (top.set_index("timestamp")
                  .resample("1min")
                  .agg(open=("price","first"),
                       high=("price","max"),
                       low =("price","min"),
                       close=("price","last"),
                       volume=("size","sum"))
                ).dropna(subset=["open","high","low","close"])
    return ohlcv_1m

def append_parquet(df_ohlcv: pd.DataFrame, asset: str, tf: str):
    p = DST_PARQUET / "hyperliquid" / asset / f"{tf}.parquet"
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        old = pd.read_parquet(p)
        df_ohlcv = pd.concat([old, df_ohlcv]).drop_duplicates().sort_index()
    df_ohlcv.to_parquet(p)

def resample_to_tf(df_1m: pd.DataFrame, tf: str) -> pd.DataFrame:
    if tf == "1m":
        return df_1m
    rule = tf_to_rule(tf)
    out = (df_1m
           .resample(rule)
           .agg(open=("open","first"),
                high=("high","max"),
                low =("low","min"),
                close=("close","last"),
                volume=("volume","sum"))
           ).dropna(subset=["open","high","low","close"])
    return out

def run_once():
    assert PAIRS_FILE.exists(), f"Falta {PAIRS_FILE}"
    cfg = yaml.safe_load(PAIRS_FILE.read_text())
    assets = [p["asset"] for p in cfg.get("pairs", [])]
    sd = yyyymmdd(HL_START)
    ed = yyyymmdd(pd.Timestamp.utcnow().strftime("%Y-%m-%d"))

    # 1) descarga → 2) descomprime → 3) CSV (repo lo define así) :contentReference[oaicite:2]{index=2}
    print(f"[INGESTOR] Rango: {sd}..{ed} Assets: {assets}", flush=True)
    run_cli("download",  assets, sd, ed)
    run_cli("decompress", assets, sd, ed)
    run_cli("to_csv",     assets, sd, ed)
    print("[INGESTOR] CSV generados. Construyendo OHLCV…", flush=True)

    # 4) para cada asset, construye OHLCV desde los CSV y exporta
    for item in cfg.get("pairs", []):
        asset   = item["asset"]
        ft_pair = item["ft_pair"]
        csv_dir = Path(f"/opt/hyperliquid-historical/CSV/{asset}")  # MAYÚSCULAS
        print(f"[INGESTOR] Leyendo CSV de: {csv_dir}", flush=True)
        df_1m   = ohlcv_from_csv_dir(csv_dir)

        for tf in TF_LIST:
            df_tf = resample_to_tf(df_1m, tf)
            append_parquet(df_tf, asset, tf)
            export_feather(df_tf, ft_pair, tf)
        print(f"[OK] {asset} → {TF_LIST}")

def main_loop():
    DST_PARQUET.mkdir(parents=True, exist_ok=True)
    DST_FEATHER.mkdir(parents=True, exist_ok=True)
    while True:
        try:
            run_once()
        except Exception as e:
            print(f"[ERROR] ciclo: {e}", file=sys.stderr)
        time.sleep(HL_LOOP_MIN * 60)

if __name__ == "__main__":
    main_loop()
