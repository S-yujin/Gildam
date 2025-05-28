import streamlit as st
from streamlit.components.v1 import html
from recommender import recommend_travel_places
from utils import load_destinations
import folium
import re
from folium import PolyLine

st.set_page_config(page_title="MYRO 스타일 부산 여행지 추천", layout="wide")
st.title("MYRO 스타일 부산 여행 플래너")
st.markdown("여행 스타일, 인원수, 일정 등을 입력하면 맞춤 여행지를 추천해드립니다.")

csv_path = "data/busan_spots.csv"
df = load_destinations(csv_path)

# 사용자 입력
user_input = st.text_area("✍️ 여행 스타일 입력", height=100)
days = st.slider("여행 일수 (1박 2일 → 2일)", min_value=1, max_value=5, value=2)

# 세션 초기화
if "raw_response" not in st.session_state:
    st.session_state["raw_response"] = ""
if "selected_places" not in st.session_state:
    st.session_state["selected_places"] = []

# 추천 버튼
if st.button("여행지 추천 받기") and user_input.strip():
    with st.spinner("추천 여행지를 찾는 중입니다..."):
        raw_response = recommend_travel_places(user_input, csv_path)
        st.session_state["raw_response"] = raw_response
        st.session_state["selected_places"] = []

raw_response = st.session_state.get("raw_response", "")
selected_places = st.session_state["selected_places"]

# 장소명 추출 함수
def extract_places(text):
    return [p.strip() for p in re.split(r"[\n,\d.\-•]+", text) if len(p.strip()) >= 2 and re.search(r"[가-힣]", p)]

# 지도 준비
m = folium.Map(location=[35.1796, 129.0756], zoom_start=11)

recommendations = []
if raw_response:
    response_list = extract_places(raw_response)
    recommendations = df[df["여행지"].isin(response_list)].to_dict(orient="records")

    # 마커 표시 + 경로 그리기
    selected_info = [r for r in recommendations if r["여행지"] in selected_places]
    if selected_info:
        chunk_size = max(1, len(selected_info) // days)
        colors = ["red", "blue", "green", "purple", "orange"]

        for i in range(0, len(selected_info), chunk_size):
            chunk = selected_info[i:i + chunk_size]
            coords = [(p["위도"], p["경도"]) for p in chunk]
            PolyLine(locations=coords, color=colors[i // chunk_size % len(colors)],
                     weight=5, opacity=0.7).add_to(m)

        for p in selected_info:
            folium.Marker([p["위도"], p["경도"]], popup=p["여행지"]).add_to(m)

map_html = m.get_root().render().replace('"', '&quot;').replace("'", "&apos;")
