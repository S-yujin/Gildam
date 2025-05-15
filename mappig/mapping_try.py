import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

st.title("GilDam")

try:
    df = pd.read_csv(r"C:\Users\leegh\Desktop\Gildam\데이터 셋/Busn_Spotdat.csv", encoding='utf-8')
except UnicodeDecodeError:
    df = pd.read_csv(r"C:\Users\leegh\Desktop\Gildam\데이터 셋/Busn_Spotdat.csv", encoding='cp949')

st.dataframe(df, height=204)

df[["lat","lon"]] = df[["위도","경도"]]

m = folium.Map(location=[35.07885, 129.04402], zoom_start=13)

marker_cluster = MarkerCluster().add_to(m)

for idx, row in df.iterrows():
    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=row["여행지"],
    ).add_to(marker_cluster)

folium_static(m)