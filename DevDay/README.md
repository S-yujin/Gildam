## 🧭 GILDAM — 감정 기반 맞춤형 부산 여행 일정 추천 서비스  
> **Emotion + Storytelling + Local Experience**  
> “감정을 출발점으로, 나만의 이야기를 가진 여행을 설계합니다.”

---

### 프로젝트 개요
- **핵심 개념:** 사용자의 감정, 테마, 여행 기간을 기반으로 AI가 부산의 숨은 명소를 추천하고, 일정·지도·이유를 함께 제시하는 감성 여행 일정 생성 서비스  
- **목표:** 비인기·로컬 관광지 노출 확대와 감정 기반 여행 경험 제공  
- **기술 스택:**
  - 백엔드: **Flask**
  - 프론트엔드: **HTML + CSS + JavaScript (Vanilla)**
  - 감정·추천 엔진: **Google Gemini API (REST)**
  - 데이터: **부산 관광·맛집·축제·쇼핑 통합 CSV**
  - 지도: **Leaflet.js + OpenStreetMap**

---

### 의존성 설치
```bash
pip install -r backend/requirements.txt

```
## 1) API 키 설정
환경변수 `GEMINI_API_KEY` 설정

### A) .env 파일 (권장)
프로젝트 루트에 `.env` 생성
```
GEMINI_API_KEY="여기에_키"
```

### B) Windows PowerShell
```powershell
setx GEMINI_API_KEY "여기에_키"
```

## 2) 실행
```bash
python backend/app.py
```
→ http://127.0.0.1:8000

## 3) 엔드포인트
- `POST /api/emotion`  { text } → { emotions: [...] }
- `POST /api/recommend` { emotions, themes, date } → { items: [...] }


지도 구성 바꿈
 -> 글? 구도? 내용? 바꿔야 함.
    -> 프롬포트, CSS (이미지)
home에 사진 추가하기 -> 지도 완성본 캡쳐해서 추가.
