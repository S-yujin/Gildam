import streamlit as st
from recommender import recommend_travel_places
from utils import load_destinations
import pandas as pd

st.set_page_config(page_title="부산 여행지 추천", layout="wide")

st.title("부산 여행지 추천")
st.markdonw("여행스타일과 정보를 입력하면 여행지를 추천해줍니다!")

user_input = st.text_input("여행 스타일, 인원수, 일정 등을 입력하세요:", height=100)
csv_path = "data/busan_spots.csv"

if st.button("여행지 추천 받기") and user_input.strip():
    with st.spinner("추천 여행지를 찾는 중입니다..."):
        raw_response = recommend_travel_places(user_input, csv_path)

    st.subheader("추천 여행지")
    df = load_destinations(csv_path)

    selected_palces = []

    for idx, row in df.iterrows():
        place_name = row["여행지명"]
        title = row["제목"]
        subtitle = row["부제목"]
        thumbmail = row["썸네일"]
        if place_

if __name__ == "__main__":
    user_input = input("여행 스타일, 인원수, 일정 등을 입력하세요: ")
    csv_path = "data/busan_spots.csv"

    recommendations = recommend_travel_places(user_input, csv_path)
    print("추천 여행지:")
    print(recommendations)