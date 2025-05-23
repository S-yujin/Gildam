import pandas as pd

def load_destinations(filepath: str) -> pd.DataFrame:
    return pd.read_csv(filepath)

def format_data_for_prompt(df: pd.DataFrame) -> str:
    lines = []
    for _, row in df.iterrows():
        place = row.get('여행지 명', '알 수 없음')
        title = row.get('제목', '없음')
        subtitle = row.get('부제목', '없음')
        lines.append(f"장소명: {place}, 제목: {title}, 부제목: {subtitle}")
    return "\n".join(lines)
