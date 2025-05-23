# 필요한 라이브러리 임포트
import streamlit as st
from recommender import recommend_travel_places  # 여행지 추천 함수
from utils import load_destinations              # CSV 데이터 로딩 함수
import pandas as pd

# 페이지 설정: 제목 및 레이아웃 지정
st.set_page_config(page_title="부산 여행지 추천", layout="wide")

# 앱 제목 및 설명
st.title("부산 여행지 추천")
st.markdown("여행스타일과 정보를 입력하면 여행지를 추천해줍니다!")

# 사용자 입력 필드 (여행 스타일, 인원수, 일정 등)
user_input = st.text_area("여행 스타일, 인원수, 일정 등을 입력하세요:", height=100)
csv_path = "data/busan_spots.csv"  # 여행지 데이터가 저장된 CSV 경로

# 버튼 클릭 시 추천 시작
if st.button("여행지 추천 받기") and user_input.strip():
    with st.spinner("추천 여행지를 찾는 중입니다..."):
        # Gemini 기반 추천 결과 문자열을 반환
        raw_response = recommend_travel_places(user_input, csv_path)

    # 추천 결과 출력 구간
    st.subheader("추천 여행지")

    # 여행지 데이터 로딩
    df = load_destinations(csv_path)

    selected_places = []  # 사용자가 선택한 장소를 저장할 리스트

    # 여행지 데이터를 순회하며 추천된 항목만 필터링
    for idx, row in df.iterrows():
        place_name = row["여행지"]
        title = row["제목"]
        subtitle = row["부제목"]
        thumbnail = row["썸네일이미지URL"]

        # 추천 응답에 포함된 장소만 표시
        if place_name in raw_response:
            col1, col2 = st.columns([1, 4])  # 이미지와 텍스트를 좌우로 분할
            with col1:
                # 썸네일 이미지가 있는 경우 출력
                if pd.notna(thumbnail) and thumbnail.startswith("http"):
                    st.image(thumbnail, width=120)
            with col2:
                # 체크박스로 사용자 선택 가능
                checked = st.checkbox(f"**{place_name}** - {title}\n*{subtitle}*", key=idx)
                if checked:
                    selected_places.append(place_name)

    # 선택된 장소 목록 출력
    if selected_places:
        st.markdown("### 선택한 여행지:")
        for place in selected_places:
            st.markdown(f"- {place}")
