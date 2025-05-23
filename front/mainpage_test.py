import streamlit as st
from mapping_try import render_map
from chat import start_chat


def main():
    st.title("메인 페이지")

    # 2개의 열로 나누기 (왼쪽: 지도 / 오른쪽: 챗봇)
    col1, col2 = st.columns([1, 2])  # 비율 조절 가능
    
    with col1:
        st.subheader("💬 챗봇")
        start_chat()
        

    with col2:
        st.subheader("🗺️ 지도")
        render_map()

if __name__ == "__main__":
    main()