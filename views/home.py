import streamlit as st
from views.common_style import set_button_style, set_logo

def render(go_to):
    set_logo()
    set_button_style()

    st.markdown("""
        <style>
        #MainMenu, footer, header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="text-align:center; margin-top:200px; font-size:32px; font-weight:bold;">
        당신의 스토리에 맞는 여행을 찾아보세요!
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        st.markdown("<div style='margin-top:150px;'></div>", unsafe_allow_html=True)
        if st.button("시작하기"):
            st.query_params.clear()
            go_to("purpose")
