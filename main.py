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

st.set_page_config(page_title="MYRO 부산 여행지 추천", layout="wide")
st.title("MYRO 스타일 부산 여행 플래너")

csv_path = "data/busan_spots.csv"
df = load_destinations(csv_path)

user_input = st.text_area("✍️ 여행 스타일 입력", height=100)
days = st.slider("여행 일수", 1, 5, 2)

if "raw_response" not in st.session_state:
    st.session_state["raw_response"] = ""
if "selected" not in st.session_state:
    st.session_state["selected"] = set()
if "reasons" not in st.session_state:
    st.session_state["reasons"] = {}

if st.button("여행지 추천 받기") and user_input.strip():
    with st.spinner("추천 중입니다..."):
        st.session_state["raw_response"] = recommend_travel_places(user_input, csv_path)
        st.session_state["selected"] = set()
        st.session_state["reasons"] = {}

def extract_places(text):
    lines = re.split(r"[\n,]", text)
    cleaned = [re.sub(r"^[\s\-\u2022\d.\u2460-\u2473]*", "", line).strip() for line in lines]
    return [p for p in cleaned if p and re.search(r"[\uac00-\ud7a3]", p)]

def fuzzy_match_places(response, df):
    extracted = extract_places(response)
    matched = []
    for place in df["여행지"]:
        for line in extracted:
            if place in line:
                matched.append(place)
                break
    return matched

raw_response = st.session_state["raw_response"]
recommendations = []
if raw_response:
    matched_names = fuzzy_match_places(raw_response, df)
    recommendations = df[df["여행지"].isin(matched_names)].to_dict(orient="records")

def render_map_per_day(selected_info, days, mode="all"):
    m = folium.Map(location=[35.1796, 129.0756], zoom_start=12)
    if not selected_info:
        return m

    chunk_size = max(1, len(selected_info) // days)
    chunks = [selected_info[i:i + chunk_size] for i in range(0, len(selected_info), chunk_size)]
    colors = ["red", "blue", "green", "purple", "orange"]

    for day_idx, chunk in enumerate(chunks):
        if mode != "all" and mode != f"day{day_idx+1}":
            continue

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

left_col, right_col = st.columns([1, 1], gap="large")

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

            if place not in st.session_state["reasons"]:
                with st.spinner("추천 이유 생성 중..."):
                    st.session_state["reasons"][place] = generate_reason_llm(title, subtitle)

            reason = st.session_state["reasons"].get(place, "")
            st.markdown(f"💡 **추천 이유**: {reason}")

            review_data = get_place_rating_and_review(place)
            st.markdown(f"⭐ **평점**: {review_data['rating']}")
            if review_data["reviews"]:
                st.markdown(f"🗣 **리뷰**: {review_data['reviews'][0]}")
            checked = st.checkbox("지도에 표시", key=f"{place}_{idx}",
                                  value=place in st.session_state["selected"])
            if checked:
                st.session_state["selected"].add(place)
            else:
                st.session_state["selected"].discard(place)
        st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    st.subheader("🗺 지도에서 확인")
    selected_info = [r for r in recommendations if r["여행지"] in st.session_state["selected"]]

    if days == 1:
        map_obj = render_map_per_day(selected_info, days=1, mode="all")
        st_folium(map_obj, width=700, height=600, key="map_all_single_day")
    else:
        tab_labels = ["전체"] + [f"{i+1}일차" for i in range(days)]
        tabs = st.tabs(tab_labels)

        with tabs[0]:
            map_obj = render_map_per_day(selected_info, days=days, mode="all")
            st_folium(map_obj, width=700, height=600, key="map_all")

        for i in range(1, days + 1):
            with tabs[i]:
                map_obj = render_map_per_day(selected_info, days=days, mode=f"day{i}")
                st_folium(map_obj, width=700, height=600, key=f"map_day_{i}")