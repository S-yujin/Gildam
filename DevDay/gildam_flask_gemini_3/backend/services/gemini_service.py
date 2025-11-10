import logging
import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Union

import pandas as pd
import requests
from packaging import version as _v

import google.generativeai as genai
from backend.config import Config
from backend.services.prompt_templates import PromptTemplates

logger = logging.getLogger(__name__)

# --- Gemini SDK 초기화 ---
genai.configure(api_key=Config.GEMINI_API_KEY)

# --- 데이터 경로 ---
CSV_PATH = Path(Config.DATA_CSV_PATH)

def _best_filled_column(df: pd.DataFrame, candidates: List[str]) -> pd.Series:
    """여러 후보 중 '존재하고 non-null이 가장 많은' 컬럼을 선택해 반환"""
    cols = [c for c in candidates if c in df.columns]
    if not cols:
        return pd.Series([None] * len(df))
    cols.sort(key=lambda c: df[c].notna().sum(), reverse=True)
    return df[cols[0]]

# 데이터 로딩 / 전처리

def _load_master_df() -> pd.DataFrame:
    """CSV 파일 로드 및 전처리"""
    logger.info("=" * 60)
    logger.info("📂 CSV 파일 로드 시작.")
    logger.info(f"   경로: {CSV_PATH}")

    try:
        df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
        logger.info(f"✅ CSV 로드 성공: {len(df)}행")
    except Exception as e:
        logger.error(f"❌ CSV 로드 실패: {e}")
        raise

    df.columns = df.columns.str.strip()

    def col(df, *names):
        for n in names:
            if n in df.columns:
                return df[n]
        return pd.Series([None] * len(df))

    def s(x):
        if pd.isna(x):
            return ""
        sx = str(x).strip()
        if sx.lower() in {"null", "none", "nan"}:
            return ""
        return sx

    # 다양한 컬럼명을 허용 (사용자 CSV 호환)
    name = col(df, "콘텐츠명", "제목", "name", "장소명")
    gu = col(df, "구군", "gu", "구")
    lat = pd.to_numeric(col(df, "위도", "latitude", "lat"), errors="coerce")
    lng = pd.to_numeric(col(df, "경도", "longitude", "lng", "lon"), errors="coerce")
    address = _best_filled_column(df, ["주소", "주소 기타", "주소 기타 ", "장소", "address"])
    raw_type = col(df, "유형", "여행지", "type", "타입")
    detail = col(df, "상세내용", "detail", "설명")
    subtitle = col(df, "부제", "부제목", "subtitle")
    spot = col(df, "주요장소", "spot")
    place = col(df, "장소", "place")
    rep_menu = col(df, "대표메뉴", "menu", "메뉴")

    master = pd.DataFrame(
        {
            "name": name.apply(s),
            "gu": gu.apply(s),
            "latitude": lat,
            "longitude": lng,
            "address": address.apply(s),
            "raw_type": raw_type.apply(s),
            "rep_menu": rep_menu.apply(s),
            "keywords": (
                detail.apply(s)
                + " "
                + subtitle.apply(s)
                + " "
                + spot.apply(s)
                + " "
                + place.apply(s)
            ).str.strip(),
        }
    )

    # 좌표 유효값만 (부산 대략 범위)
    master = master.dropna(subset=["latitude", "longitude"])
    master = master[
        (master["latitude"].between(34.8, 36.2))
        & (master["longitude"].between(128.5, 130.0))
    ]

    # 초유명 스팟 제외 (비주류 중심)
    ban = ["해운대", "광안리", "감천문화마을", "자갈치", "국제시장", "BIFF"]
    patt = "|".join(ban)
    master = master[~master["name"].str.contains(patt, case=False, na=False)]

    # 간단 카테고리 추론
    def guess_category(row):
        text = f"{row['name']} {row['raw_type']} {row['keywords']}"
        if "카페" in text:
            return "카페"
        if row["rep_menu"]:
            return "식당"
        if any(kw in text for kw in ["체험", "공방", "워크샵"]):
            return "체험"
        if any(kw in text for kw in ["쇼핑", "상점", "마켓"]):
            return "쇼핑"
        return "관광지"

    master["category"] = master.apply(guess_category, axis=1)

    cat_counts = master["category"].value_counts()
    logger.info("   카테고리별 개수:")
    for cat, cnt in cat_counts.items():
        logger.info(f"     - {cat}: {cnt}개")

    logger.info("=" * 60)
    return master.reset_index(drop=True)


def _filter_candidates(master_df: pd.DataFrame, themes, days: int) -> pd.DataFrame:
    """테마에 맞는 후보 필터링 (일정 길이에 따라 동적 조정)"""
    logger.info("=" * 60)
    logger.info(f"🔍 후보 필터링 시작 (테마: {themes}, 일수: {days})")

    def nrm(s):
        return (s or "").strip().lower()

    def hit(kw):
        t = nrm(kw)
        return any(nrm(th) in t for th in (themes or []))

    df = master_df.copy()
    df["theme_hit"] = df["keywords"].apply(hit)
    df["rank"] = df["theme_hit"].astype(int) * 3

    hit_count = df["theme_hit"].sum()
    logger.info(f"   테마 매칭: {hit_count}개")

    # 하루당 5~6곳, 안전계수 3, 최대 60
    max_candidates = min(days * 6 * 3, 60)

    filtered = df.sort_values("rank", ascending=False).head(max_candidates * 2)

    categories = {
        "관광지": int(max_candidates * 0.4),
        "식당": int(max_candidates * 0.25),
        "카페": int(max_candidates * 0.2),
        "체험": int(max_candidates * 0.1),
        "쇼핑": int(max_candidates * 0.05),
    }

    result = []
    for cat, limit in categories.items():
        cat_df = filtered[filtered["category"] == cat].head(limit)
        result.append(cat_df)

    filtered = pd.concat(result, ignore_index=True)

    cat_counts = filtered["category"].value_counts()
    logger.info("   선택된 장소 카테고리:")
    for cat, cnt in cat_counts.items():
        logger.info(f"     - {cat}: {cnt}개")

    logger.info("=" * 60)
    return filtered[
        ["name", "address", "latitude", "longitude", "category", "keywords", "gu"]
    ].reset_index(drop=True)


# =========================
# Gemini 호출 서비스 (교체본)
# =========================
class GeminiService:
    def __init__(self):
        logger.info("🤖 GeminiService 초기화.")
        self.generation_config = {
            "temperature": 0.8,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
        }

        # 모델명은 호출 직전에 자동 선택 (ListModels)
        self.model_name: Union[str, None] = None

        # SDK 사용 가능 여부
        self._use_sdk = False
        try:
            sdk_ver = getattr(genai, "__version__", "0.0.0")
            logger.info(f"   google-generativeai SDK 버전: {sdk_ver}")
            if _v.parse(sdk_ver) >= _v.parse("1.0.0"):
                self._use_sdk = True
                logger.info("✅ SDK(v1) 사용 가능")
            else:
                logger.warning("⚠️ SDK 0.x(v1beta) → REST(v1) 우회 예정")
        except Exception as e:
            logger.warning(f"⚠️ SDK 체크 실패 → REST 우회: {e}")
            self._use_sdk = False

    # --- 모델 자동 선택 ---
    def _pick_model_name(self) -> str:
        api_key = Config.GEMINI_API_KEY
        url = "https://generativelanguage.googleapis.com/v1/models"
        headers = {"x-goog-api-key": api_key}

        # 신→구 선호순 (호환성 고려해 1.5 먼저 시도하도록 아래 REST에서 재정렬함)
        preferred = [
            "models/gemini-2.5-flash",
            "models/gemini-2.0-flash",
            "models/gemini-1.5-flash",
            "models/gemini-1.5-flash-8b",
            "models/gemini-1.5-pro",
            "models/gemini-pro",
        ]

        try:
            r = requests.get(url, headers=headers, timeout=30)
            r.raise_for_status()
            data = r.json()
            models = {m["name"]: m for m in data.get("models", [])}

            def supports_generate(m):
                ops = m.get("supportedGenerationMethods") or m.get("generation_methods")
                return bool(ops and ("generateContent" in ops))

            candidates = [name for name, meta in models.items() if supports_generate(meta)]

            logger.info(f"   🔎 사용가능 모델 수: {len(candidates)}")
            for p in preferred:
                if p in candidates:
                    logger.info(f"   ✅ 선택된 모델: {p}")
                    return p

            if candidates:
                choice = candidates[0]
                logger.info(f"   ⚠️ 선호 목록엔 없음 → {choice} 사용")
                return choice

            raise RuntimeError("사용 가능한 Gemini 모델이 없습니다. (ListModels 결과 비어 있음)")

        except requests.HTTPError as e:
            logger.error(f"   ❌ ListModels 실패: {e}")
            return "models/gemini-1.5-flash"
        except Exception as e:
            logger.error(f"   ❌ ListModels 예외: {e}")
            return "models/gemini-1.5-flash"

    # --- v1 REST 호출 (견고 버전) ---
    def _rest_generate_content(self, prompt: str) -> str:
        api_key = Config.GEMINI_API_KEY
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        }

        if not self.model_name:
            self.model_name = self._pick_model_name()

        def to_full_name(name: str) -> str:
            return name if name.startswith("models/") else f"models/{name}"

        # 호환성 좋은 1.5 계열 먼저
        model_candidates = [
            "models/gemini-1.5-flash",
            "models/gemini-1.5-pro",
            "models/gemini-1.5-flash-8b",
            "models/gemini-pro",
            "models/gemini-2.0-flash",
            "models/gemini-2.5-flash",
        ]
        # pick 결과를 맨 앞에 끼워넣기
        if self.model_name not in model_candidates:
            model_candidates.insert(0, self.model_name)

        base_min = [{"parts": [{"text": prompt}]}]
        base_role = [{"role": "user", "parts": [{"text": prompt}]}]

        payload_variants = [
            {"contents": base_min},  # #1 미니멀
            {"contents": base_role},  # #2 role 포함
            {"contents": base_min,    # #3 gen config
             "generationConfig": {
                 "temperature": self.generation_config.get("temperature", 0.8),
                 "topP": self.generation_config.get("top_p", 0.95),
                 "maxOutputTokens": self.generation_config.get("max_output_tokens", 2048),
             }},
            {"contents": base_role,   # #4 gen config + safety (최후)
             "generationConfig": {
                 "temperature": self.generation_config.get("temperature", 0.8),
                 "topP": self.generation_config.get("top_p", 0.95),
                 "maxOutputTokens": self.generation_config.get("max_output_tokens", 2048),
             },
             "safetySettings": [
                 {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                 {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                 {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                 {"category": "HARM_CATEGORY_SEXUAL_CONTENT", "threshold": "BLOCK_NONE"},
             ]},
        ]

        tried_models = set()
        all_errors = []

        for cand_model in model_candidates:
            name = to_full_name(cand_model)
            if name in tried_models:
                continue
            tried_models.add(name)

            url = f"https://generativelanguage.googleapis.com/v1/{name}:generateContent"

            for idx, payload in enumerate(payload_variants, 1):
                try:
                    logger.info(f"   ▶ 모델 {name} / 페이로드#{idx} 시도")
                    r = requests.post(url, headers=headers, json=payload, timeout=60)

                    if r.status_code == 404:
                        logger.warning(f"   ⚠️ 404 Not Found (model): {name} → 다른 모델 시도")
                        all_errors.append(f"404:{name}")
                        break  # 다음 모델로

                    if r.status_code == 400:
                        err_text = (r.text or "")[:800]
                        logger.error(f"   ❌ 400 Bad Request (payload#{idx}) for {name} | body: {err_text}")
                        all_errors.append(f"400:{name}#p{idx}")
                        continue  # 다음 페이로드

                    if r.status_code >= 300:
                        err_text = (r.text or "")[:800]
                        logger.error(f"   ❌ HTTP {r.status_code} for {name} (payload#{idx}) | body: {err_text}")
                        all_errors.append(f"{r.status_code}:{name}#p{idx}")
                        continue

                    data = r.json()

                    if "promptFeedback" in data:
                        logger.info(f"   ℹ️ promptFeedback: {data['promptFeedback']}")

                    cands = data.get("candidates", [])
                    if not cands:
                        logger.warning(f"   ⚠️ candidates 비어있음 (model={name}, payload#{idx}) → 다음 시도")
                        all_errors.append(f"emptyCands:{name}#p{idx}")
                        continue

                    text = "".join(
                        part.get("text", "")
                        for cand in cands
                        for part in (cand.get("content", {}) or {}).get("parts", [])
                    ).strip()

                    if not text:
                        logger.warning(f"   ⚠️ parts[].text 비어있음 (model={name}, payload#{idx}) → 다음 시도")
                        all_errors.append(f"emptyText:{name}#p{idx}")
                        continue

                    logger.info(f"   ✅ 성공 (model={name}, payload#{idx})")
                    return text

                except requests.HTTPError as e:
                    body = getattr(e.response, "text", "")[:800]
                    logger.error(f"   ❌ HTTPError {e} (model={name}, payload#{idx}) | body: {body}")
                    all_errors.append(f"HTTP:{name}#p{idx}")
                except Exception as e:
                    logger.error(f"   ❌ 예외 {type(e).__name__}: {e} (model={name}, payload#{idx})")
                    all_errors.append(f"EX:{name}#p{idx}")

        raise RuntimeError(f"모든 모델/페이로드 호출 실패. 시도 모델 수: {len(tried_models)} / 에러: {all_errors}")

    # --- 외부 진입점 (반드시 클래스 내부 메서드로 유지!) ---
    def generate_itinerary(self, trip_data: Dict[str, Any]) -> Union[Dict, None]:
        """일정 생성 with 재시도 + Rate Limit 처리"""
        logger.info("=" * 60)
        logger.info("🚀 일정 생성 시작")
        logger.info(f"   기간: {trip_data.get('start')} ~ {trip_data.get('end')}")
        logger.info(f"   일수: {trip_data.get('days')}일")
        logger.info(f"   감정: {trip_data.get('emotions')}")
        logger.info(f"   테마: {trip_data.get('themes')}")
        logger.info("=" * 60)

        max_retries = 3

        # 후보 데이터 준비
        try:
            master = _load_master_df()
            candidates = _filter_candidates(
                master, trip_data.get("themes", []), trip_data.get("days", 1)
            )
        except Exception as e:
            logger.error(f"❌ 데이터 로드 실패: {e}")
            import traceback; traceback.print_exc()
            return None

        for attempt in range(max_retries):
            try:
                logger.info(f"\n🔄 시도 {attempt + 1}/{max_retries}")

                if attempt > 0:
                    wait_time = 35
                    logger.info(f"   ⏳ Rate limit 대기 중. ({wait_time}초)")
                    time.sleep(wait_time)

                logger.info("   📝 프롬프트 생성 중.")
                prompt = PromptTemplates.get_itinerary_prompt(trip_data, candidates)
                logger.info(f"   ✅ 프롬프트 생성 완료 (길이: {len(prompt)}자)")

                logger.info("   🤖 Gemini 호출 중...")
                if self._use_sdk:
                    if not self.model_name:
                        self.model_name = self._pick_model_name()
                    sdk_model = self.model_name.replace("models/", "")
                    try:
                        model = genai.GenerativeModel(
                            sdk_model, generation_config=self.generation_config
                        )
                        response = model.generate_content(prompt)
                        response_text = getattr(response, "text", "")
                        logger.info(f"   ✅ SDK 응답 (길이: {len(response_text)}자)")
                    except Exception as e:
                        logger.error(f"   ❌ SDK 호출 실패: {e}")
                        logger.info("   🔁 REST(v1)로 폴백")
                        response_text = self._rest_generate_content(prompt)
                else:
                    response_text = self._rest_generate_content(prompt)

                logger.info("   📄 응답 내용 (처음 1000자):")
                logger.info("-" * 60)
                logger.info(response_text[:1000])
                logger.info("-" * 60)

                logger.info("   🔍 응답 파싱 중.")
                result = self._parse_response(response_text)
                if not result:
                    logger.warning("   ❌ 파싱 실패 - 재시도")
                    continue

                logger.info("   ✅ 파싱 성공")
                logger.info("   📊 파싱된 데이터 구조:")
                logger.info(f"      - summary: {result.get('summary', 'N/A')[:100]}.")
                logger.info(f"      - itinerary 개수: {len(result.get('itinerary', []))}")

                if result.get("itinerary"):
                    for i, day in enumerate(result["itinerary"], 1):
                        logger.info(f"        {i}일차: {len(day.get('places', []))}개 장소")

                logger.info("   🔍 일정 검증 중.")
                if self._validate_itinerary(result, trip_data):
                    logger.info("   ✅ 검증 성공!")
                    logger.info("=" * 60)
                    logger.info("🎉 일정 생성 완료!")
                    logger.info("=" * 60)
                    return result
                else:
                    logger.warning("   ❌ 검증 실패, 재시도.")

            except Exception as e:
                error_msg = str(e)
                logger.error(f"   ❌ 오류 발생: {type(e).__name__}: {error_msg}")

                if "429" in error_msg or "ResourceExhausted" in error_msg:
                    logger.warning("   ⚠️ API Rate Limit 도달")
                    if attempt < max_retries - 1:
                        logger.info("   ⏳ 35초 대기 후 재시도.")
                        time.sleep(35)
                        continue

                import traceback; traceback.print_exc()

                if attempt == max_retries - 1:
                    logger.warning("   🔄 Fallback 일정 생성.")
                    return self._get_fallback_itinerary(trip_data, candidates)

        logger.error("❌ 모든 시도 실패")
        return self._get_fallback_itinerary(trip_data, candidates)

    # --- 응답 파싱 ---
    def _parse_response(self, text: str) -> Union[Dict[str, Any], None]:
        try:
            if not text or not text.strip():
                logger.error("      ❌ 응답이 비어있음(response_text=''). 모델이 텍스트를 생성하지 않았습니다.")
                return None

            text = text.strip()
            logger.info(f"      응답 시작 부분: {text[:200]}.")

            # ```json ... ``` 제거
            json_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
            if json_match:
                text = json_match.group(1)
                logger.info("      ✅ Markdown 코드 블록 제거")

            # 첫 번째 {} 블록만 추출
            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            if json_match:
                text = json_match.group(0)

            data = json.loads(text)
            logger.info("      ✅ JSON 파싱 성공")
            return data

        except json.JSONDecodeError as e:
            logger.error(f"      ❌ JSON 파싱 실패: {e}")
            logger.error(f"      문제 위치: line {e.lineno}, col {e.colno}")
            return None
        except Exception as e:
            logger.error(f"      ❌ 예상치 못한 오류: {e}")
            return None

    # --- 결과 검증 ---
    def _validate_itinerary(self, data: Dict[str, Any], trip_data: Dict[str, Any]) -> bool:
        if not isinstance(data, dict):
            logger.error("      ❌ 응답이 dict가 아님")
            return False
        if "itinerary" not in data:
            logger.error("      ❌ 'itinerary' 키 없음")
            logger.error(f"      실제 키: {list(data.keys())}")
            return False

        itinerary = data["itinerary"]
        if not isinstance(itinerary, list):
            logger.error("      ❌ itinerary가 list가 아님")
            return False
        if len(itinerary) != trip_data["days"]:
            logger.error(f"      ❌ 일수 불일치: {len(itinerary)} != {trip_data['days']}")
            return False

        def hhmm_ok(s):
            return isinstance(s, str) and len(s) == 5 and s[2] == ":" and s[:2].isdigit() and s[3:].isdigit()

        for i, day_plan in enumerate(itinerary, 1):
            if not isinstance(day_plan, dict):
                logger.error(f"      ❌ {i}일차가 dict가 아님"); return False

            places = day_plan.get("places", [])
            if not isinstance(places, list) or not places:
                logger.error(f"      ❌ {i}일차 장소가 비어있음"); return False

            for j, place in enumerate(places, 1):
                required = ["name","address","latitude","longitude","start_time","end_time","category","duration","reason"]
                missing = [k for k in required if k not in place]
                if missing:
                    logger.error(f"      ❌ {i}일차 {j}번째 장소에 필수 필드 누락: {missing}")
                    return False

                if not hhmm_ok(place["start_time"]) or not hhmm_ok(place["end_time"]):
                    logger.error(f"      ❌ {i}일차 {j}번째 장소의 시간 형식 오류"); return False

                try:
                    float(place["latitude"]); float(place["longitude"])
                except Exception as e:
                    logger.error(f"      ❌ {i}일차 {j}번째 장소의 좌표 형식 오류: {e}"); return False

        logger.info(f"      ✅ 모든 검증 통과 ({len(itinerary)}일)")
        return True

    # --- 폴백 ---
    def _get_fallback_itinerary(self, trip_data: Dict[str, Any], candidates: pd.DataFrame) -> Dict[str, Any]:
        logger.warning("🔄 Fallback 일정 생성")
        import datetime

        start_date = datetime.datetime.strptime(trip_data["start"], "%Y-%m-%d")
        places_per_day = min(6, max(1, len(candidates) // max(trip_data["days"], 1)))
        itinerary: List[Dict[str, Any]] = []

        for day_num in range(trip_data["days"]):
            current_date = start_date + datetime.timedelta(days=day_num)
            start_idx = day_num * places_per_day
            end_idx = start_idx + places_per_day
            sample_places = candidates.iloc[start_idx:end_idx].to_dict("records")

            base_places: List[Dict[str, Any]] = []
            current_time = datetime.time(9, 0)

            for place in sample_places:
                start = current_time.strftime("%H:%M")
                duration = 90 if place["category"] == "식당" else 60
                end_time = (datetime.datetime.combine(datetime.date.today(), current_time)
                            + datetime.timedelta(minutes=duration)).time()

                base_places.append({
                    "name": place["name"],
                    "address": place["address"],
                    "latitude": float(place["latitude"]),
                    "longitude": float(place["longitude"]),
                    "start_time": start,
                    "end_time": end_time.strftime("%H:%M"),
                    "duration": duration,
                    "category": place["category"],
                    "reason": f"{place['category']} 추천 장소입니다.",
                })

                current_time = (datetime.datetime.combine(datetime.date.today(), end_time)
                                + datetime.timedelta(minutes=30)).time()

            itinerary.append({
                "day": day_num + 1,
                "date": current_date.strftime("%Y-%m-%d"),
                "title": f"{day_num + 1}일차 일정",
                "places": base_places,
            })

        logger.info(f"✅ Fallback 일정 생성 완료 ({len(itinerary)}일)")
        return {
            "summary": f"{(trip_data.get('emotions') or ['여유로운'])[0]} 부산 여행 일정입니다.",
            "itinerary": itinerary,
        }
