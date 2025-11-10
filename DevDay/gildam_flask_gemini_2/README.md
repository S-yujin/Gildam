# 감정 기반 관광지 추천 (Flask + Gemini, no Uvicorn)

- **서버**: Flask (내장 서버 사용 → `python backend/app.py`)
- **프론트**: HTML/CSS/JS
- **감정 분석**: Google Gemini REST API
- **데이터**: 부산 관광데이터

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



데이터 추가하기
프롬포트 다듬기
카톡으로 공유하기 버튼 만들기
지도 카드랑 목록 카드 길이 맞추기
 -> 짜피 비율이랑 구성 바꿀 거임
home에 사진 추가하기
전체적으로 글 정돈 및 수정하기
------------------------------
도메인 예쁘게?