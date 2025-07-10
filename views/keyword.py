import streamlit as st
from views.common_style import set_logo, set_button_style

def render(go_to):
    set_logo()
    set_button_style()

    st.markdown("<h2 style='text-align:center;'>현재 당신의 감정을 선택해주세요</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>(다중 선택 가능)</p>", unsafe_allow_html=True)

    emotions = [
    "🌿 힐링", "💓 설렘", "😭 감동", "🛋️ 편안함", "🍃 여유", "😊 행복",
    "🧘‍♀️ 휴식", "😁 기쁨", "😞 우울", "😡 분노", "😰 불안", "💔 상실감",
    "😔 외로움", "😣 스트레스"]

    if "selected_emotions" not in st.session_state:
        st.session_state.selected_emotions = set()

    st.markdown("### 감정을 선택하세요:")

    cols = st.columns(4)
    for idx, emotion in enumerate(emotions):
        col = cols[idx % 4]
        with col:
            checked = emotion in st.session_state.selected_emotions
            if st.checkbox(emotion, value=checked, key=f"emotion_{emotion}"):
                st.session_state.selected_emotions.add(emotion)
            else:
                st.session_state.selected_emotions.discard(emotion)

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<div style='margin-top:50px;'></div>", unsafe_allow_html=True)
        if st.button("다음"):
            if st.session_state.selected_emotions:
                st.session_state["emotion"] = list(st.session_state.selected_emotions)
                go_to("theme")
            else:
                st.warning("한 가지 이상 선택해주세요.")
