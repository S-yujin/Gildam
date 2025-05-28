import pandas as pd
import requests
from googletrans import Translator
import streamlit as st
from config import GOOGLE_PLACES_API_KEY

# CSV 파일 로딩
def load_destinations(filepath: str) -> pd.DataFrame:
    return pd.read_csv(filepath)

# Gemini 프롬프트용 문자열 구성
def format_data_for_prompt(df: pd.DataFrame) -> str:
    lines = []
    for _, row in df.iterrows():
        place = row.get('여행지 명', '알 수 없음')
        title = row.get('제목', '없음')
        subtitle = row.get('부제목', '없음')
        lines.append(f"장소명: {place}, 제목: {title}, 부제목: {subtitle}")
    return "\n".join(lines)

# Google 리뷰 및 평점 조회 함수 (번역 포함, 캐시 사용)
translator = Translator()

@st.cache_data(show_spinner=False)
def get_place_rating_and_review(place_name: str, location: str = "Busan, South Korea") -> dict:
    search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": f"{place_name}, {location}",
        "key": GOOGLE_PLACES_API_KEY,
    }

    res = requests.get(search_url, params=params)
    results = res.json().get("results", [])
    if not results:
        return {"rating": "N/A", "reviews": []}

    place_id = results[0].get("place_id")
    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
    detail_params = {
        "place_id": place_id,
        "key": GOOGLE_PLACES_API_KEY,
        "fields": "rating,reviews"
    }

    detail_res = requests.get(details_url, params=detail_params)
    detail_json = detail_res.json().get("result", {})

    rating = detail_json.get("rating", "N/A")
    reviews_raw = detail_json.get("reviews", [])[:2]
    reviews_translated = []

    for review in reviews_raw:
        text = review.get("text", "")
        if text:
            translated = translator.translate(text, dest="ko").text
            if len(translated) > 100:
                translated = translated[:100] + "..."
            reviews_translated.append(translated)

    return {
        "rating": rating,
        "reviews": reviews_translated
    }