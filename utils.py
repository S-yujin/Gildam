# 데이터 처리 유틸리티 함수 모음
import pandas as pd
import requests
import os
import googletrans
from googletrans import Translator
from config import GOOGLE_PLACES_API_KEY

# CSV 파일을 DataFrame으로 로드
def load_destinations(filepath: str) -> pd.DataFrame:
    return pd.read_csv(filepath)

# 여행지 데이터를 프롬프트 형식에 맞춰 문자열로 변환
def format_data_for_prompt(df: pd.DataFrame) -> str:
    lines = []
    for _, row in df.iterrows():
        place = row.get('여행지 명', '알 수 없음')
        title = row.get('제목', '없음')
        subtitle = row.get('부제목', '없음')
        lines.append(f"장소명: {place}, 제목: {title}, 부제목: {subtitle}")
    return "\n".join(lines)

translator = Translator()

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

    # 평점
    rating = detail_json.get("rating", "N/A")

    # 리뷰 2개 추출, 한국어로 번역 및 요약
    reviews_raw = detail_json.get("reviews", [])[:2]
    reviews_translated = []

    for review in reviews_raw:
        text = review.get("text", "")
        if text:
            # 번역 (영어 → 한국어)
            translated = translator.translate(text, dest='ko').text
            # 간단히 100자 이내로 요약
            if len(translated) > 100:
                translated = translated[:100] + "..."
            reviews_translated.append(translated)

    return {
        "rating": rating,
        "reviews": reviews_translated
    }