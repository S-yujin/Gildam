import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

def ask_gemini(prompt: str) -> str:
    model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")  
    response = model.generate_content(prompt)
    return response.text
