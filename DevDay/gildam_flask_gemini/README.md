# 감정 기반 관광지 추천 (Flask + Gemini, no Uvicorn)

- **서버**: Flask (내장 서버 사용 → `python backend/app.py`)
- **프론트**: HTML/CSS/JS
- **감정 분석**: Google Gemini REST API
- **데이터**: 부산 샘플 10건 (CSV→Parquet 변환 1회)

## 1) 설치
```bash
pip install -r backend/requirements.txt
```

## 2) API 키 설정
환경변수 `GEMINI_API_KEY` 설정

### A) .env 파일 (권장)
프로젝트 루트에 `.env` 생성 (`.env.sample` 참고)
```
GEMINI_API_KEY="여기에_키"
```

### B) Windows PowerShell
```powershell
setx GEMINI_API_KEY "여기에_키"
```

## 3) 실행
```bash
python backend/app.py
```
→ http://127.0.0.1:8000

## 4) 엔드포인트
- `POST /api/emotion`  { text } → { emotions: [...] }
- `POST /api/recommend` { emotions, themes, date } → { items: [...] }
