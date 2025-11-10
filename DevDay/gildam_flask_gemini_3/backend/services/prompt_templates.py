from typing import List, Dict, Any, Union
import pandas as pd

class PromptTemplates:
    # 감정/테마 표현 사전
    EMOTION_STYLES = {
        '차분': '조용하고 평화로운',
        '힐링': '여유롭고 편안한',
        '로맨틱': '감성적이고 아름다운',
        '들뜸': '활기차고 재미있는',
        '활기': '에너지 넘치는',
        '우울': '위로가 되는 따뜻한',
    }

    THEME_KEYWORDS = {
        '바다': '해변, 해안가, 오션뷰',
        '자연': '공원, 숲길, 자연경관',
        '산책': '걷기 좋은 길, 프롬나드',
        '전망': '뷰포인트, 전망대, 스카이라인',
        '야경': '야경 명소, 야간 조명',
        '역사': '문화재, 박물관, 전통',
        '공방/체험': '핸드메이드, 체험 프로그램',
        '카페': '감성 카페, 디저트',
        '시장/맛집': '로컬 맛집, 전통시장',
        '축제': '이벤트, 문화행사',
        '쇼핑': '상점가, 편집숍',
        '포토스팟': '인스타그래머블, 사진 명소',
    }

    @staticmethod
    def _coalesce(v, default=""):
        return default if v is None else v

    @staticmethod
    def _render_candidates_block(candidates: Union[pd.DataFrame, List[Dict[str, Any]]]) -> str:
        """
        candidates를 모델 컨텍스트용 텍스트 블록으로 변환.
        """
        rows: List[Dict[str, Any]]
        if isinstance(candidates, pd.DataFrame):
            cols = ["name", "address", "latitude", "longitude", "category", "keywords", "gu"]
            missing = [c for c in cols if c not in candidates.columns]
            if missing:
                raise ValueError(f"candidates DataFrame에 누락된 컬럼이 있습니다: {missing}")
            rows = candidates[cols].to_dict(orient="records")
        else:
            rows = []
            for i, r in enumerate(candidates):
                for k in ["name", "address", "latitude", "longitude", "category", "keywords", "gu"]:
                    if k not in r:
                        raise ValueError(f"candidates[{i}]에 '{k}' 키가 없습니다.")
                rows.append(r)

        lines: List[str] = []
        for r in rows:
            name = str(PromptTemplates._coalesce(r.get("name", ""))).strip()
            address = str(PromptTemplates._coalesce(r.get("address", ""))).strip()
            lat = r.get("latitude", "")
            lng = r.get("longitude", "")
            category = str(PromptTemplates._coalesce(r.get("category", ""))).strip()
            keywords = str(PromptTemplates._coalesce(r.get("keywords", ""))).strip()
            gu = str(PromptTemplates._coalesce(r.get("gu", ""))).strip()

            if len(keywords) > 220:
                keywords = keywords[:220].rstrip() + "…"

            lines.append(
                f"- name:{name} | address:{address} | lat:{lat},lng:{lng} | category:{category} | keywords:{keywords} | gu:{gu}"
            )
        return "\n".join(lines)

    @staticmethod
    def get_itinerary_prompt(
        data: Dict[str, Any],
        candidates: Union[pd.DataFrame, List[Dict[str, Any]]]
    ) -> str:
        """
        감정과 테마에 따른 맞춤형 프롬프트
        """
        emotions = data.get("emotions", []) or []
        themes = data.get("themes", []) or []
        days = int(data.get("days", 1) or 1)
        nights = int(data.get("nights", max(days - 1, 0)))
        start = str(data.get("start", "YYYY-MM-DD"))
        end = str(data.get("end", "YYYY-MM-DD"))
        purpose = str(data.get("purpose", "")).strip()

        emotion_desc = ", ".join([PromptTemplates.EMOTION_STYLES.get(e, e) for e in emotions]) or "사용자 감정"
        theme_desc = ", ".join([PromptTemplates.THEME_KEYWORDS.get(t, t) for t in themes]) or "선택 테마"

        # ✅ 수정: candidates를 실제로 렌더링
        filtered_places = PromptTemplates._render_candidates_block(candidates)

        PROMPT = """
당신은 **부산 지역 전문 여행 플래너 AI**입니다.
아래 제공된 **실제 장소 목록 내부에서만** 일정을 구성하세요. 목록에 없는 장소는 절대 생성하지 마세요.

---

## 🧭 여행자 프로필 (입력)
- 여행 기간: {start} ~ {end} ({nights}박 {days}일)
- 여행 목적: {purpose}
- 현재 감정 상태: {emotion_desc}
- 원하는 테마: {theme_desc}

---

## 📂 사용 가능한 장소 목록 (필수 제약)
아래는 추천 가능한 **실제 장소 데이터**입니다.
**반드시 이 목록 안에서만 선택**하고, 아래 필드들을 **원문 그대로** 사용하세요.

{filtered_places}

> 각 항목은 최소한 다음 필드를 가집니다:
> `name`, `address`, `latitude`, `longitude`, `category`, `keywords`, `gu`

---

## ⚙️ 엄격 규칙 (하나라도 위반하면 전체 출력을 다시 생성하라)

1) **목록 내부만 사용**
   - 반드시 위 “사용 가능한 장소 목록” 안의 장소만 선택.
   - 장소명, 주소, 좌표, 카테고리는 **입력 목록 값 그대로** 복사 사용(철자/띄어쓰기 변경 금지).
   - 목록에 없는 장소/주소/좌표/카테고리는 **금지**.

2) **비인기 스팟 우선**
   - 입력 목록은 이미 초유명 스팟을 제외함.
   - 로컬/한적/뷰 포인트를 우선 반영.

3) **감정·테마 매칭**
   - '{emotion_desc}' 분위기를 반영하고 '{theme_desc}'와 관련된 장소만 포함.
   - 장소 선택 근거는 각 장소의 `keywords`에서 테마·감정과의 연결성을 우선 찾되, 약하면 제외.

4) **동선 최적화 (부산 지리 준수)**
   - 하루는 **서로 가까운 곳**으로 묶기. 가능하면 같은 `gu` 중심.
   - **하루 이동 반경 ≤ 10km** 유지(대략적으로라도 가까운 군집을 우선).
   - 중복 방문 금지(장소명 중복 X).

5) **시간대 구성 (운영 상식 준수)**
   - 1일차 시작: **09:00~10:00 사이**
   - 마지막 날 종료: **17:00 이전**
   - **점심(12:00~14:00), 저녁(18:00~20:00)은 반드시 `식당` 포함**
   - `카페`는 보통 10:00~22:00, `관광지`는 일몰 전에 종료하도록 합리적으로 배치
   - 하루 총 5~6곳 권장(여유 있는 루트)

6) **카테고리 균형(권장)**
   - 예시(하루): 관광지 2~3, 식당 2(점심·저녁), 카페 0~1
   - 체험/쇼핑은 테마·감정과 맞으면 적절히 포함

7) **시간/형식 유효성**
   - 모든 시간은 "HH:MM"(24시간제, 0패딩)
   - 각 장소는 start_time < end_time, duration(분)은 양의 정수
   - latitude, longitude는 숫자(float)
   - 매 날짜별 장소 배열은 **시간 순서(오름차순)**

8) **출력 형식 (JSON only)**
   - JSON 외 텍스트·마크다운·주석 금지
   - 지정 스키마의 키 이름/대소문자 정확히 지킬 것
   - 필드 누락/빈 문자열/"null"/"NaN" 금지(주소·이름 반드시 채움)

---

## ✅ 출력 스키마 (정확히 이 구조만)

{{
  "summary": "이번 여행은 {emotion_desc}한 분위기로 {theme_desc} 중심의 일정입니다.",
  "itinerary": [
    {{
      "day": 1,
      "date": "{start}",
      "title": "첫날 제목",
      "places": [
        {{
          "name": "장소 이름(목록 그대로)",
          "address": "주소(목록 그대로)",
          "latitude": 35.xxxx,
          "longitude": 129.xxxx,
          "start_time": "09:00",
          "end_time": "10:30",
          "duration": 90,
          "category": "관광지",
          "reason": "감정/테마와의 연결 근거를 1~2문장으로 간결히",
          "tips": "선택사항: 현지 팁/시간대/좌석/대기/포토스팟 등"
        }}
      ]
    }}
  ]
}}

> 주의: 각 날짜(day=1..{days}, date는 해당 날짜)마다 **5~6개** places를 채워 작성.
> 마지막 날은 반드시 17:00 이전 종료, 매일 점심·저녁 식당 포함.

---

## 🔎 사전 점검 체크리스트
- 장소명/주소/좌표/카테고리 → **모두 목록 값과 정확히 일치**
- 하루 이동 반경이 10km 이내로 군집되었는가?
- 모든 날짜에 점심·저녁 식당이 포함되었는가?
- 마지막 날 종료 시간이 17:00 이전인가?
- 모든 시간이 "HH:MM" 형식이며 start_time < end_time인가?
- 각 날짜 5~6개 장소, 전체 중복 장소 없음이 보장되는가?
- 출력은 오직 JSON 한 덩어리인가?

---

## ⛔ 절대 금지
- 목록에 없는 장소/주소/좌표 생성
- JSON 외 텍스트/마크다운/코멘트/사과문
- null, "null", 빈 문자열, 잘못된 시간/좌표
- 하루 이동 반경 10km 이상 과도 이동

---

## 🎯 생성 목표
- {emotion_desc} 감정과 {theme_desc} 테마에 정확히 부합하는 부산의 **숨은 명소 중심 일정**
- 현실적 시간표, 합리적 동선, 균형 잡힌 카테고리
- 파서가 바로 쓸 수 있는 **정합성 높은 JSON** 생성

**지금 위 조건을 모두 충족하는 JSON만 출력하세요.**
"""

        return PROMPT