import pandas as pd
from utils.cache import cache
from data.loader import DATAFRAME

EMOTION_W = {"행복":1.0, "설렘":0.9, "힐링":0.9, "우울":-0.5, "지루함":-0.4}
THEME_W   = {"자연":0.8, "바다":1.0, "카페":0.6, "산책":0.7, "문화":0.8}

def _contains_any(cell, selected):
    if not selected:
        return False
    if isinstance(cell, str):
        tokens = [t.strip() for t in cell.split(",")]
    elif isinstance(cell, (list, tuple, set)):
        tokens = list(cell)
    else:
        tokens = []
    return any(t in tokens for t in selected)

def _score_row(row, emotions, themes):
    e = sum(EMOTION_W.get(x, 0) for x in emotions if _contains_any(row.get("emotion_tags",""), [x]))
    t = sum(THEME_W.get(x, 0)   for x in themes   if _contains_any(row.get("theme_tags",""), [x]))
    base = float(row.get("base_popularity", 0.3))
    return base + e + t

@cache(ttl=300)
def recommend_places(emotions, themes, date=None, k=20):
    df = DATAFRAME.copy()
    if emotions:
        df = df[df["emotion_tags"].apply(lambda s: _contains_any(s, emotions))]
    if themes:
        df = df[df["theme_tags"].apply(lambda s: _contains_any(s, themes))]
    if df.empty:
        df = DATAFRAME.copy()

    df["score"] = df.apply(lambda r: _score_row(r, emotions, themes), axis=1)
    out = (
        df.sort_values("score", ascending=False)
          .head(k)[["name","category","district","score","tags"]]
          .copy()
    )
    out["tags"] = out["tags"].apply(lambda x: x if isinstance(x, list) else [])
    return out.to_dict(orient="records")
