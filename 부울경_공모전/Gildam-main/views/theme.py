import streamlit as st
from views.common_style import set_logo, set_button_style

def render(go_to):
    set_logo()
    set_button_style()

    st.markdown("<h2 style='text-align:center;'>이번 여행에서 원하는 테마를 선택해주세요</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>(다중 선택 가능)</p>", unsafe_allow_html=True)

    themes = [
    "🌳 자연", "🍽️ 맛집", "🎨 예술", "🏛️ 역사", "🏖️ 휴양", "🏃 액티비티",
    "🎭 문화", "🌃 야경", "🧘 힐링", "💑 로맨틱", "👵 효도", "🧗 모험"]

    if "selected_themes" not in st.session_state:
        st.session_state.selected_themes = set()

    st.markdown("### 테마를 선택하세요:")

    cols = st.columns(4)
    for idx, theme in enumerate(themes):
        col = cols[idx % 4]
        with col:
            checked = theme in st.session_state.selected_themes
            if st.checkbox(theme, value=checked, key=f"theme_{theme}"):
                st.session_state.selected_themes.add(theme)
            else:
                st.session_state.selected_themes.discard(theme)

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<div style='margin-top:50px;'></div>", unsafe_allow_html=True)
        if st.button("다음"):
            if st.session_state.selected_themes:
                st.session_state["theme"] = list(st.session_state.selected_themes)
                go_to("recommend")
            else:
                st.warning("한 가지 이상 선택해주세요.")
