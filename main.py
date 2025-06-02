import streamlit as st
import re
import folium
from streamlit_folium import st_folium
from recommender import recommend_travel_places
from utils import (
    load_destinations,
    get_place_rating_and_review,
    generate_reason_llm
)

# 페이지 설정
st.set_page_config(page_title="MYRO 부산 여행지 추천", layout="wide")
st.title("MYRO 스타일 부산 여행 플래너")

# 데이터 로드
csv_path = "data/busan_spots.csv"
df = load_destinations(csv_path)

# 사용자 입력 받기
user_input = st.text_area("✍️ 여행 스타일 입력", height=100)
days = st.slider("여행 일수", 1, 5, 2)

# 세션 상태 초기화
if "raw_response" not in st.session_state:
    st.session_state["raw_response"] = ""
if "selected" not in st.session_state:
    st.session_state["selected"] = set()
if "reasons" not in st.session_state:
    st.session_state["reasons"] = {}

# 추천 버튼 클릭 시 Gemini를 통해 추천 실행
if st.button("여행지 추천 받기") and user_input.strip():
    with st.spinner("추천 중입니다..."):
        st.session_state["raw_response"] = recommend_travel_places(user_input, csv_path)
        st.session_state["selected"] = set()
        st.session_state["reasons"] = {}

# 응답에서 여행지 이름 추출
def extract_places(text):
    lines = re.split(r"[\n,]", text)
    cleaned = [re.sub(r"^[\s\-\u2022\d.\u2460-\u2473]*", "", line).strip() for line in lines]
    return [p for p in cleaned if p and re.search(r"[\uac00-\ud7a3]", p)]

# 데이터프레임과 매칭되는 장소 이름만 필터링
def fuzzy_match_places(response, df):
    extracted = extract_places(response)
    matched = []
    for place in df["여행지"]:
        for line in extracted:
            if place in line:
                matched.append(place)
                break
    return matched

# 추천 결과 매칭
raw_response = st.session_state["raw_response"]
recommendations = []
if raw_response:
    matched_names = fuzzy_match_places(raw_response, df)
    recommendations = df[df["여행지"].isin(matched_names)].to_dict(orient="records")

# 지도 렌더링 함수: 일자별로 색상 구분
def render_map_per_day(selected_info, days, mode="all"):
    m = folium.Map(location=[35.1796, 129.0756], zoom_start=12)
    if not selected_info:
        return m

    # 선택된 장소를 여행 일수만큼 나눔
    chunk_size = max(1, len(selected_info) // days)
    chunks = [selected_info[i:i + chunk_size] for i in range(0, len(selected_info), chunk_size)]
    colors = ["red", "blue", "green", "purple", "orange"]

    for day_idx, chunk in enumerate(chunks):
        if mode != "all" and mode != f"day{day_idx+1}":
            continue

        # 경로 연결 (Polyline) 및 마커 추가
        coords = [(p["위도"], p["경도"]) for p in chunk]
        folium.PolyLine(
            locations=coords,
            color=colors[day_idx % len(colors)],
            weight=5,
            opacity=0.8,
            tooltip=f"{day_idx+1}일차 경로"
        ).add_to(m)

        for idx, p in enumerate(chunk, 1):
            place = p["여행지"]
            title = p["제목"]
            subtitle = p["부제목"]
            popup_html = f"<b>{place}</b><br>{title}<br>{subtitle}"

            folium.Marker(
                location=[p["위도"], p["경도"]],
                popup=popup_html,
                tooltip=f"{day_idx+1}일차 - {place}"
            ).add_to(m)

    return m

# 카드 UI 스타일 정의 (HTML/CSS)
st.markdown("""
    <style>
    .recommend-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 15px;
        background-color: #f9f9f9;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# 좌우 컬럼 분할: 왼쪽에 추천 카드, 오른쪽에 지도
left_col, right_col = st.columns([1, 1], gap="large")

# 추천 여행지 카드 출력
with left_col:
    st.subheader("📋 추천 여행지")
    for idx, p in enumerate(recommendations):
        st.markdown('<div class="recommend-card">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 3])

        with col1:
            st.image(p["썸네일이미지URL"], width=100)

        with col2:
            place = p["여행지"]
            title = p["제목"]
            subtitle = p["부제목"]
            st.markdown(f"**{place}**")

            # 추천 이유 생성 (LLM 호출, 캐시)
            if place not in st.session_state["reasons"]:
                with st.spinner("추천 이유 생성 중..."):
                    st.session_state["reasons"][place] = generate_reason_llm(title, subtitle)

            reason = st.session_state["reasons"].get(place, "")
            st.markdown(f"💡 **추천 이유**: {reason}")

            # Google Place API로 별점 및 리뷰 가져오기
            review_data = get_place_rating_and_review(place)
            st.markdown(f"⭐ **평점**: {review_data['rating']}")
            if review_data["reviews"]:
                st.markdown(f"🗣 **리뷰**: {review_data['reviews'][0]}")

            # 체크박스로 지도 표시 여부 제어
            checked = st.checkbox("지도에 표시", key=f"{place}_{idx}",
                                  value=place in st.session_state["selected"])
            if checked:
                st.session_state["selected"].add(place)
            else:
                st.session_state["selected"].discard(place)

        st.markdown('</div>', unsafe_allow_html=True)

# 오른쪽: 지도 표시
with right_col:
    st.subheader("🗺 지도에서 확인")
    selected_info = [r for r in recommendations if r["여행지"] in st.session_state["selected"]]

    # 일자별 지도 탭 분할
    if days == 1:
        map_obj = render_map_per_day(selected_info, days=1, mode="all")
        st_folium(map_obj, width=700, height=600, key="map_all_single_day")
    else:
        tab_labels = ["전체"] + [f"{i+1}일차" for i in range(days)]
        tabs = st.tabs(tab_labels)

        # 전체 경로 탭
        with tabs[0]:
            map_obj = render_map_per_day(selected_info, days=days, mode="all")
            st_folium(map_obj, width=700, height=600, key="map_all")

        # 각 일차별 경로 탭
        for i in range(1, days + 1):
            with tabs[i]:
                map_obj = render_map_per_day(selected_info, days=days, mode=f"day{i}")
                st_folium(map_obj, width=700, height=600, key=f"map_day_{i}")
