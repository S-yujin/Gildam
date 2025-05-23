# Gemini API 호출을 담당하는 함수 정의
import google.generativeai as genai
from config import GEMINI_API_KEY

# API 키 설정
genai.configure(api_key=GEMINI_API_KEY)

# 프롬프트를 기반으로 Gemini 모델로부터 응답 받기
def ask_gemini(prompt: str) -> str:
    model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")
    response = model.generate_content(prompt)
    return response.text