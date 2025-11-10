import streamlit as st
import base64
from streamlit.components.v1 import html

def set_button_style():
    st.markdown("""
        <style>
        div.stButton > button {
            width: 600px;
            height: 60px;
            font-size: 20px;
            border-radius: 16px;
            background-color: #2997D8 !important;
            color: white !important;
            border: none;
        }
        div.stButton > button:hover {
            background-color: #1a6f9c !important;
        }
        </style>
    """, unsafe_allow_html=True)


def inject_custom_css_js(items, key_name):
    st.markdown("""
        <style>
        .custom-btn {
            border: 2px solid #ccc;
            border-radius: 20px;
            padding: 10px 24px;
            margin: 10px;
            font-size: 16px;
            cursor: pointer;
            background-color: white;
            color: black;
            transition: all 0.2s ease-in-out;
        }
        .custom-btn:hover {
            background-color: #f0f0f0;
        }
        .custom-btn.selected {
            border-color: #1E90FF;
            color: white;
            background-color: #1E90FF;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

    button_html = ""
    for item in items:
        button_html += f'<button class="custom-btn" onclick="toggleSelect(this)" data-key="{item}">{item}</button>'

    js_code = f"""
    <div>{button_html}</div>
    <script>
    let selected = [];
    function toggleSelect(el) {{
        const key = el.getAttribute("data-key");
        if (selected.includes(key)) {{
            selected = selected.filter(k => k !== key);
            el.classList.remove("selected");
        }} else {{
            selected.push(key);
            el.classList.add("selected");
        }}
        const input = window.parent.document.querySelector('input[name="{key_name}"]');
        if (input) {{
            input.value = selected.join(",");
            input.dispatchEvent(new Event("input", {{ bubbles: true }}));
        }}
    }}
    </script>
    """
    st.markdown(js_code, unsafe_allow_html=True)

def set_logo():
    image_path = "data/logo_gildam.png"  # 로고 이미지 경로

    # 이미지 Base64 인코딩
    with open(image_path, "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode()

    st.markdown(f"""
        <style>
        .logo-fixed {{
            position: fixed;
            top: 20px;
            left: 20px;
            z-index: 9999;
        }}
        .logo-fixed img {{
            height: 70px;
            cursor: pointer;
        }}

        /* 작은 화면일 경우 top 위치 조정 */
        @media screen and (max-width: 900px) {{
            .logo-fixed {{
                top: 60px;
                left: 10px;
            }}
            .logo-fixed img {{
                height: 60px;
            }}
        }}

        /* 아주 작은 모바일 화면 */
        @media screen and (max-width: 600px) {{
            .logo-fixed {{
                top: 80px;
                left: 5px;
            }}
            .logo-fixed img {{
                height: 50px;
            }}
        }}
        </style>

        <a href="?logo_home=1" target="_self">
            <div class="logo-fixed">
                <img src="data:image/png;base64,{img_base64}" alt="길담 로고">
            </div>
        </a>
    """, unsafe_allow_html=True)

wide_card_style = """
    background-color: #f8f9fa;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0 0 8px rgba(0, 0, 0, 0.1);
    margin-bottom: 15px;
"""


def render_share_button():
    st.markdown("""
        <style>
        .share-btn {
            background-color: #4f8dfd;
            color: white;
            padding: 10px 20px;
            font-size: 16px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            margin-top: 20px;
        }
        .share-btn:hover {
            background-color: #2f6ad9;
        }
        </style>
    """, unsafe_allow_html=True)

    html("""
        <button class="share-btn" onclick="copyCurrentUrl()">🔗 공유하기</button>
        <script>
        function copyCurrentUrl() {
            const dummy = document.createElement('input');
            const url = window.location.href;
            document.body.appendChild(dummy);
            dummy.setAttribute('value', url);
            dummy.select();
            document.execCommand('copy');
            document.body.removeChild(dummy);
            alert("📎 현재 링크가 클립보드에 복사되었습니다!");
        }
        </script>
    """)