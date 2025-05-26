import streamlit as st
from recommender import recommend_travel_places
from utils import load_destinations, get_place_rating_and_review
from mapping_try import render_map
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="부산 여행지 추천", layout="wide")

st.title("부산 여행지 추천")
st.markdown("여행스타일과 정보를 입력하면 여행지를 추천해줍니다!")

# 사용자 입력
user_input = st.text_area("여행 스타일, 인원수, 일정 등을 입력하세요:", height=100)
csv_path = "data/busan_spots.csv"

# 세션 초기화
if "raw_response" not in st.session_state:
    st.session_state["raw_response"] = ""
if "selected_places" not in st.session_state:
    st.session_state["selected_places"] = []

# 추천 버튼 클릭 시
if st.button("여행지 추천 받기") and user_input.strip():
    with st.spinner("추천 여행지를 찾는 중입니다..."):
        raw_response = recommend_travel_places(user_input, csv_path)
        st.session_state["raw_response"] = raw_response
        st.session_state["selected_places"] = []  # 이전 선택 초기화

raw_response = st.session_state.get("raw_response", "")
selected_places = st.session_state.get("selected_places", [])

# 추천된 여행지 표시
if raw_response:
    st.subheader("추천 여행지")
    df = load_destinations(csv_path)

    for idx, row in df.iterrows():
        place_name = row["여행지"]
        title = row["제목"]
        subtitle = row["부제목"]
        thumbnail = row["썸네일이미지URL"]

        if place_name in raw_response:
            col1, col2 = st.columns([1, 4])
            with col1:
                if pd.notna(thumbnail) and thumbnail.startswith("http"):
                    st.image(thumbnail, width=120)
            with col2:
                checked = st.checkbox(f"**{place_name}** - {title}\n*{subtitle}*", key=idx)
                if checked and place_name not in selected_places:
                    selected_places.append(place_name)
                elif not checked and place_name in selected_places:
                    selected_places.remove(place_name)

                # 평점 및 리뷰 표시
                try:
                    place_info = get_place_rating_and_review(place_name)
                    st.markdown(f"⭐ 평점: {place_info['rating']}")
                    for review in place_info["reviews"]:
                        st.markdown(f"- _{review}_")
                except Exception as e:
                    st.markdown("_리뷰 정보를 불러오지 못했습니다._")

    st.session_state["selected_places"] = selected_places

# 선택한 여행지 지도 보기
if selected_places:
    # 2개의 열로 나누기 (왼쪽: 지도 / 오른쪽: 챗봇)
    col1, col2 = st.columns([1, 2])  # 비율 조절 가능
    
    with col1:
        st.markdown("### 선택한 여행지:")
        for place in selected_places:
            st.markdown(f"- {place}")

    with col2:
    # if st.button("🗺 선택한 여행지 지도에 보기"):
        st.markdown("#### 여행지 지도")
        render_map(selected_places, csv_path=csv_path)
        
