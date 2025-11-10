import streamlit as st
import pandas as pd
import json
import re
import folium
from streamlit_folium import st_folium
from gemini_api import ask_gemini
from .common_style import set_logo, render_share_button

set_logo()

# 카드 스타일 정의 (회색 배경)
wide_card_style = """
<style>
.wide-card {
    background-color: #f8f9fa;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}
.wide-card h4 {
    margin-top: 0;
    color: #333;
}
.wide-card ul {
    padding-left: 20px;
}
</style>
"""

# 로딩 오버레이 스타일 추가
loading_overlay_style = """
<style>
.overlay {
    position: fixed;
    top: 0; left: 0;
    width: 100vw;
    height: 100vh;
    background-color: white;
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
}
.loading-text {
    font-size: 2.5rem;
    color: #4f8dfd;
    animation: blink 1s infinite;
}
@keyframes blink {
    0% { opacity: 1; }
    50% { opacity: 0.3; }
    100% { opacity: 1; }
}
</style>
<div class="overlay">
    <div class="loading-text">🗺️ 여행지를 추천 중입니다...</div>
</div>
"""

# 세션 상태 초기화
if 'schedule' not in st.session_state:
    st.session_state['schedule'] = {'start': '2025-07-12', 'end': '2025-07-14'}
if 'purpose' not in st.session_state:
    st.session_state['purpose'] = '재충전'
if 'theme' not in st.session_state:
    st.session_state['theme'] = ['자연과 함께']
if 'emotion' not in st.session_state:
    st.session_state['emotion'] = ['힐링']
if 'keywords' not in st.session_state:
    st.session_state['keywords'] = ['감성']
if 'recommend_ready' not in st.session_state:
    st.session_state['recommend_ready'] = False

@st.cache_data
def load_dataset():
    return pd.read_csv("data/부산_명소_축제_통합.csv", encoding='utf-8')

def build_prompt(emotion, purpose, schedule, theme, df):
    content_blocks = []
    for _, row in df.iterrows():
        combined_text = f"제목: {row['제목']}\n부제목: {row['부제목']}\n상세내용: {row['상세내용']}"
        content_blocks.append(f"콘텐츠명: {row['콘텐츠명']}\n{combined_text}")

    prompt = f"""
    당신은 감정 기반 여행지 추천을 전문으로 하는 여행 설계 전문가입니다.
    특히, 부산 지역의 숨은 명소와 감성적인 장소를 중심으로,
    사용자의 감정 상태와 여행 목적, 일정, 선호 테마에 맞는 여정을 스토리텔링 형태로 구성하는 역할을 맡고 있습니다.

    📌 다음과 같은 원칙을 반드시 지켜야 합니다:

    1. **추천 장소는 반드시 제공된 콘텐츠 목록에 있는 '콘텐츠명'과 정확히 일치해야 합니다.**
    2. **각 추천 장소는 제목, 부제목, 상세내용을 참고하여 서사적으로 표현합니다.**
    3. **추천 문장은 감성적이며 따뜻하고 공감 가능한 문체로 작성하며, 객관적 정보보다 정서적 묘사에 집중합니다.**
    4. **추천 장소는 너무 유명한 관광지는 피하고, 감정과 어울리는 숨은 명소, 고즈넉한 분위기의 장소를 우선합니다.**
    5. **각 장소는 여행 일정의 동선을 고려하여 추천 순서를 배치하며, 축제도 일정 날짜와 맞는 경우에만 추천이 가능합니다.**
    6. **모든 표현은 사용자와 대화하듯, 부드럽고 정서적인 어조로 작성합니다.** (예: "바다 내음이 가득한 이곳에서 잠시 멈춰 서보세요…")

    🧳 사용자 정보:
    - 감정 상태: {', '.join(emotion)}
    - 여행 목적: {purpose}
    - 일정: {schedule['start']} ~ {schedule['end']}
    - 선호 테마: {', '.join(theme)}

    🗂 추천할 수 있는 콘텐츠 목록은 다음과 같습니다:
    {chr(10).join(content_blocks)}

    🎯 출력은 다음과 같은 JSON 리스트 형식으로 작성하세요 (3~6개 이상):

    [
    {{
    "place": "콘텐츠명",  // 콘텐츠 목록 중 하나와 정확히 일치
    "title": "감성 키워드가 담긴 한 줄 제목",  // 예: "조용한 위로가 머무는 골목길"
    "story": "감정 키워드, 장소 분위기, 추천 활동을 서사 형식으로 3~6줄 이내 감성적으로 묘사", 
    "best_time": "낮 | 밤 | 해질 무렵 등",
    "day": 1  // 여행 순서에 따른 추천일 (정수)
    }},
    ...
    ]

    📌 예시:

    [
    {{
    "place": "송도해상케이블카",
    "title": "하늘과 바다가 만나는 위로의 순간",
    "story": "푸른 바다 위를 천천히 지나가는 케이블카에서 바라보는 풍경은, 지친 마음을 조용히 어루만집니다.  
            투명한 유리 아래 펼쳐진 바닷빛은 새로운 설렘으로 가득하고, 바람을 따라 흐르는 시간 속에서 힐링을 마주하게 됩니다.  
            '힐링'을 원하는 당신에게, 이곳은 잊지 못할 감정을 선물할 거예요.",
    "best_time": "해질 무렵",
    "day": 1
    }},
    {{
    "place": "흰여울문화마을",
    "title": "햇살이 스미는 벽화의 골목길",
    "story": "좁은 골목을 따라 펼쳐진 벽화와 바다의 조화는, 낯선 여행지에서 편안함을 느끼게 해줍니다.  
            계단을 오를 때마다 펼쳐지는 풍경은 마치 마음속 풍경을 꺼내는 듯하고, 고요한 마을의 정취가 감성을 자극합니다.  
            햇살 좋은 낮에 걷다 보면, 마음속 깊은 여유가 피어납니다.",
    "best_time": "낮",
    "day": 1
    }}
    ]

    """
    return prompt

def render(go_to):
    st.markdown("### 🛫 여행지 추천 결과")
    df = load_dataset()

    if not st.session_state.get("recommend_ready"):
        st.markdown(loading_overlay_style, unsafe_allow_html=True)
        emotion = st.session_state['emotion']
        purpose = st.session_state['purpose']
        schedule = st.session_state['schedule']
        theme = st.session_state['theme']

        prompt = build_prompt(emotion, purpose, schedule, theme, df)

        with st.spinner("AI가 여행지를 추천중입니다..."):
            try:
                raw_response = ask_gemini(prompt)
                st.session_state['raw_response'] = raw_response
                st.session_state['recommend_ready'] = True
                st.rerun()
            except Exception as e:
                st.error(f"API 오류 발생: {e}")
                return

    st.markdown("---")
    st.markdown("#### ✨ 추천 여행지 목록")
    try:
        raw = st.session_state['raw_response']
        if raw.strip().startswith("```"):
            raw = re.sub(r"^```(?:json)?", "", raw).strip()
            raw = re.sub(r"```$", "", raw).strip()
        response = json.loads(raw)
    except json.JSONDecodeError:
        st.error("AI 응답을 파싱할 수 없습니다. 원문 응답을 확인합니다.")
        st.code(st.session_state['raw_response'], language='json')
        return

    valid_places = df['콘텐츠명'].dropna().unique().tolist()
    filtered_response = [item for item in response if item.get('place') in valid_places]

    if not filtered_response:
        st.warning("추천 결과가 유효한 장소와 일치하지 않습니다.")
        return

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown(wide_card_style, unsafe_allow_html=True)
        for item in filtered_response:
            name = item.get("place", "장소명 없음")
            match = df[df['콘텐츠명'] == name].iloc[0] if not df[df['콘텐츠명'] == name].empty else None
            st.markdown(f"""
                <div class="wide-card">
                    <h4>📍 {name}</h4>
                    <p><b>📖 {item.get('title', '제목 없음')}</b></p>
                    <p>{item.get('story', '스토리 없음')}</p>
                    <ul>
                        <li><b>위치:</b> {match['주소'] if match is not None and '주소' in match else '정보 없음'}</li>
                        <li><b>방문 추천 시간:</b> {item.get('best_time', '정보 없음')}</li>
                        <li><b>추천 일차:</b> {item.get('day', 'N/A')}일차</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)

    with col2:
        m = folium.Map(location=[35.1796, 129.0756], zoom_start=12)
        coords_by_day = {}
        day_colors = ['blue', 'green', 'purple', 'orange', 'red']

        for item in filtered_response:
            name = item.get("place")
            day = int(item.get("day", 1))
            row = df[df['콘텐츠명'] == name]
            if not row.empty:
                lat, lon = row.iloc[0]["위도"], row.iloc[0]["경도"]
                if pd.notna(lat) and pd.notna(lon):
                    folium.Marker(
                        location=[lat, lon],
                        popup=folium.Popup(f"<b>{name}</b><br>{item.get('reason', '')}", max_width=300),
                        icon=folium.Icon(color=day_colors[(day - 1) % len(day_colors)])
                    ).add_to(m)
                    coords_by_day.setdefault(day, []).append((lat, lon))

        for day, coords in coords_by_day.items():
            if len(coords) >= 2:
                folium.PolyLine(coords, color=day_colors[(day - 1) % len(day_colors)], weight=4).add_to(m)

        st_folium(m, width=700, height=500)
        render_share_button()