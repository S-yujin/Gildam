
def render_map(selected_places, csv_path="data/busan_spots.cvs"):
    import streamlit as st
    import pandas as pd
    import folium
    from streamlit_folium import folium_static
    from folium.plugins import MarkerCluster

    df = pd.read_csv(csv_path)
    df = df[df["여행지"].isin(selected_places)]
    df[["lat","lon"]] = df[["위도","경도"]]
    
    #맵생성
    m = folium.Map(
        location=[35.07885, 129.04402],
        zoom_start=13,
        tiles='CartoDB positron',
        preset="barcelona",
        dpi=200)

    #마커달기
    marker_cluster = MarkerCluster().add_to(m)

    for _, row in df.iterrows():
        folium.Marker(
            location=[row["lat"], row["lon"]],
            popup=row["여행지"],
        ).add_to(marker_cluster)

    folium_static(m)