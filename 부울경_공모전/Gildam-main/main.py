import streamlit as st
st.set_page_config(page_title="길담", page_icon="🌿", layout="wide")
from views import home, purpose, schedule, keyword, theme, recommend

#로고 클릭 시 홈으로 이동
params = st.query_params
if params.get("logo_home") == "1":
    st.session_state.page = "home"
    st.query_params.clear()

#페이지 상태 초기화
if "page" not in st.session_state:
    st.session_state.page = "home"

#페이지 이동 함수
def go_to(page_name):
    st.session_state.page = page_name
    st.query_params.clear()  # URL을 초기화하여 새로고침에도 안정성 유지

#페이지 렌더링
if st.session_state.page == "home":
    home.render(go_to)
elif st.session_state.page == "purpose":
    purpose.render(go_to)
elif st.session_state.page == "schedule":
    schedule.render(go_to)
elif st.session_state.page == "keyword":
    keyword.render(go_to)
elif st.session_state.page == "theme":
    theme.render(go_to)
elif st.session_state.page == "recommend":
    recommend.render(go_to)
