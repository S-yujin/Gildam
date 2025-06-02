import pandas as pd
import requests
from googletrans import Translator
import streamlit as st
from config import GOOGLE_PLACES_API_KEY
from gemini_api import ask_gemini

# CSV 파일 로딩
def load_destinations(filepath: str) -> pd.DataFrame:
    return pd.read_csv(filepath)

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

# LLM을 사용해 추천 이유 생성
def generate_reason_llm(title: str, subtitle: str) -> str:
    if not title and not subtitle:
        return "부산에서 꼭 가볼 만한 장소예요!"

    prompt = f"""
다음 장소의 제목과 부제목을 기반으로 매력적인 추천 이유 문장을 1~2문장으로 만들어줘.
형식은 사용자에게 설명하듯 자연스러운 구어체로, 문장은 간결하고 따뜻한 느낌으로 해줘.
- 제목: {title}
- 부제목: {subtitle}
"""
    return ask_gemini(prompt).strip()