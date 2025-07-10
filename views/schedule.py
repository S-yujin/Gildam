import streamlit as st
from datetime import date
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
        <h2 style="text-align:center; margin-top:80px;">여행 기간을 선택해주세요</h2>
    """, unsafe_allow_html=True)

    today = date.today()
    date_range = st.date_input(
        "여행 기간",
        value=(today, today),
        key="date_range"
    )

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<div style='margin-top:60px;'></div>", unsafe_allow_html=True)

        if st.button("다음"):
            if isinstance(date_range, tuple):
                start_date, end_date = date_range
                # 👇 핵심 조건: 종료일을 선택한 경우는 start != today 또는 end != today
                if start_date == end_date and (start_date == today and end_date == today):
                    st.warning("당일치기를 포함해도, 종료일을 명확히 선택해야 합니다.")
                elif start_date > end_date:
                    st.warning("시작일은 종료일보다 빠르거나 같아야 합니다.")
                else:
                    st.session_state["start_date"] = str(start_date)
                    st.session_state["end_date"] = str(end_date)
                    st.session_state["schedule"] = {'start': str(start_date), 'end': str(end_date)}
                    go_to("keyword")
            else:
                st.warning("여행 시작일과 종료일을 모두 선택해주세요.")
