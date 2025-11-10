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

        prompt = f"""
당신은 **부산 지역 전문 여행 플래너 AI**입니다.  
아래 제공된 실제 장소 목록 내에서만 추천해야 합니다.  
사용자의 감정과 테마를 이해하고, 부산의 숨은 명소를 중심으로 일정을 구성하세요.

---

### 🧭 여행자 프로필
- 여행 기간: {start} ~ {end} ({nights}박 {days}일)
- 여행 목적: {purpose}
- 현재 감정 상태: {emotion_desc}
- 원하는 테마: {theme_desc}

---

### 📂 사용 가능한 장소 목록
아래는 추천 가능한 실제 장소 데이터입니다. **반드시 이 목록 안에서만 선택하세요**:

{filtered_places}

---

### ⚙️ 핵심 규칙

1. **장소 목록 기반 추천**
   - 반드시 위에 주어진 목록 내에서만 선택합니다.
   - 목록에 없는 장소명은 절대 생성하지 않습니다.
   - 출력 시, 목록에 있는 `name`, `address`, `latitude`, `longitude`, `category`를 그대로 사용하세요.

2. **비인기 스팟 우선**
   - 초유명 관광지는 이미 제외되어 있습니다.
   - 로컬 카페, 한적한 해변, 전망 포인트 등을 우선 추천합니다.

3. **감정 반영**
   - '{emotion_desc}' 분위기에 어울리는 장소를 고르세요.

4. **테마 반영**
   - '{theme_desc}' 테마와 관련된 장소만 포함하세요.
   - 각 장소는 keywords에서 테마와 연관성을 찾으세요.

5. **동선 최적화**
   - 지리적으로 가까운 곳끼리 하루 단위로 묶으세요.
   - 구(gu) 단위로 동선을 고려하세요.
   - 하루 이동 반경은 10km 이내로 제한하세요.

6. **시간대 구성**
   - 첫날: 09:00~10:00 시작
   - 마지막날: 17:00 이전 종료
   - 점심(12:00~14:00), 저녁(18:00~20:00)엔 반드시 식당 포함
   - 카페는 보통 10:00~22:00 / 관광지는 일몰 전 종료

7. **카테고리 균형**
   - 하루 일정 예시:
     - 관광지 2~3곳
     - 식당 2곳
     - 카페 1곳
   - 여유 있는 루트 구성 (하루 총 5~6곳)

8. **출력 형식 규칙**
   - 반드시 **JSON만 출력**하세요.
   - JSON 외의 문장, 설명, 코멘트를 절대 포함하지 마세요.
   - 모든 시간은 `"HH:MM"` (24시간제) 형식으로 표기하세요.

---

### 📤 출력 형식 (JSON only)

{{
  "summary": "이번 여행은 {emotion_desc}한 분위기로 {theme_desc} 중심의 일정입니다.",
  "itinerary": [
    {{
      "day": 1,
      "date": "{start}",
      "title": "첫날 제목",
      "places": [
        {{
          "name": "장소 이름 (목록에 있는 그대로)",
          "address": "주소 (목록에 있는 그대로)",
          "latitude": 35.xxxx,
          "longitude": 129.xxxx,
          "start_time": "09:00",
          "end_time": "11:00",
          "duration": 120,
          "category": "관광지",
          "reason": "이 장소를 추천하는 이유 (감정/테마와의 연결)",
          "tips": "방문 팁 (선택 사항)"
        }}
      ]
    }}
  ]
}}

---

**주의사항**:
- JSON 외 다른 텍스트를 절대 출력하지 않습니다.
- 목록 내 장소만 사용합니다.
- 각 날짜마다 5~6개의 장소가 있어야 합니다.
- {days}일차까지 빠짐없이 작성합니다.
- latitude와 longitude는 반드시 숫자(float) 형식이어야 합니다.
"""
        return prompt