import pandas as pd
import requests
from googletrans import Translator  # Google 번역기 라이브러리
import streamlit as st
from config import GOOGLE_PLACES_API_KEY  # 구글 API 키
from gemini_api import ask_gemini  # Gemini LLM 호출 함수

# CSV 파일 로딩 함수
def load_destinations(filepath: str) -> pd.DataFrame:
    # 지정된 경로에서 여행지 데이터를 DataFrame으로 불러오기
    return pd.read_csv(filepath)

# Google Places API에서 장소 평점과 리뷰 가져오기
# 번역기 객체 초기화 (영어 → 한글 번역용)
translator = Translator()

@st.cache_data(show_spinner=False)  # 캐싱을 통해 반복 호출 시 속도 개선
def get_place_rating_and_review(place_name: str, location: str = "Busan, South Korea") -> dict:
    # 장소 검색 API 호출 (텍스트 기반)
    search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": f"{place_name}, {location}",
        "key": GOOGLE_PLACES_API_KEY,
    }

    res = requests.get(search_url, params=params)
    results = res.json().get("results", [])
    
    if not results:
        return {"rating": "N/A", "reviews": []}

    # 첫 번째 검색 결과의 place_id 사용
    place_id = results[0].get("place_id")

    # 장소 상세 정보 요청
    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
    detail_params = {
        "place_id": place_id,
        "key": GOOGLE_PLACES_API_KEY,
        "fields": "rating,reviews"
    }

    detail_res = requests.get(details_url, params=detail_params)
    detail_json = detail_res.json().get("result", {})

    # 평점과 리뷰 추출
    rating = detail_json.get("rating", "N/A")
    reviews_raw = detail_json.get("reviews", [])[:2]  # 최대 2개 추출
    reviews_translated = []

    # 리뷰 번역 및 길이 제한
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

# Gemini LLM을 사용하여 추천 이유 생성
def generate_reason_llm(title: str, subtitle: str) -> str:
    # 제목/부제목이 없는 경우 기본 문구 반환
    if not title and not subtitle:
        return "부산에서 꼭 가볼 만한 장소예요!"

    # 추천 이유 생성을 위한 프롬프트 구성
    prompt = f"""
다음 장소의 제목과 부제목을 기반으로 매력적인 추천 이유 문장을 1~2문장으로 만들어줘.
형식은 사용자에게 설명하듯 자연스러운 구어체로, 문장은 간결하고 따뜻한 느낌으로 해줘.
- 제목: {title}
- 부제목: {subtitle}
"""
    # Gemini API로부터 응답 받아 반환
    return ask_gemini(prompt).strip()
