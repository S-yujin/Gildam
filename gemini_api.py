import os
import google.generativeai as genai

# 환경변수나 직접 API 키 설정
GOOGLE_API_KEY = "AIzaSyCdNEXC14soYjpbZKyE059qbFBE9uhfPgY"  # 여기에 실제 Gemini API 키를 넣으세요

genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel("models/gemini-1.5-pro-latest")

def ask_gemini(prompt: str) -> str:
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"
