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

    st.markdown("<h2 style='text-align:center; margin-top:100px;'>여행 목적을 적어주세요</h2>", unsafe_allow_html=True)

    user_input = st.text_input("예: 가족과 오랜만에 맞이한 여유로운 시간. 바쁜 일상 속 서로에게 소홀했던 마음을 천천히 채워가며, 따뜻한 햇살 아래에서 함께 걷고 웃는 순간들이 하나하나 소중하게 느껴지는, 평온하고 감동적인 재충전 여행.", key="purpose_input")

    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        st.markdown("<div style='margin-top:150px;'></div>", unsafe_allow_html=True)
        if st.button("다음"):
            if user_input.strip() != "":
                st.session_state["purpose"] = user_input.strip()
                go_to("schedule")
            else:
                st.warning("목적을 입력해주세요!")
