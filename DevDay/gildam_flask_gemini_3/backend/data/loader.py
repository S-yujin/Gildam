import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent
CSV = DATA_DIR / "busan_data.csv"
PARQUET = DATA_DIR / "busan_data.parquet"

def _prepare():
    if not PARQUET.exists():
        df = pd.read_csv(CSV, encoding="utf-8")
        for c in ["category","district"]:
            if c in df.columns:
                df[c] = df[c].astype("category")
        df.to_parquet(PARQUET, index=False)
    return pd.read_parquet(PARQUET)

DATAFRAME = _prepare()
