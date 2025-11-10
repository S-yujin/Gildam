import os, requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
KNOWN = ["행복","설렘","힐링","우울","지루함"]

def analyze_emotion(text: str) -> list[str]:
    if not API_KEY:
        raise RuntimeError("환경변수 GEMINI_API_KEY 가 설정되어 있지 않습니다 (.env 또는 시스템 환경변수).")
    if not text.strip():
        return []
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    params = {"key": API_KEY}
    prompt = (
        "다음 한국어 문장에서 나타나는 감정을 아래 후보에서 골라 쉼표로만 나열해줘.\n"
        f"후보: {', '.join(KNOWN)}\n"
        "근거 설명은 하지 말고 라벨만 출력.\n"
        f"문장: {text}"
    )
    body = { "contents": [{"parts":[{"text": prompt}]}] }
    r = requests.post(url, params=params, json=body, timeout=30)
    r.raise_for_status()
    data = r.json()
    try:
        out = data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return []
    labels = [tok.strip() for tok in out.replace(" ", "").split(",") if tok.strip()]
    labels = [l for l in labels if l in KNOWN]
    return list(dict.fromkeys(labels))
