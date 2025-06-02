from gemini_api import ask_gemini
from utils import load_destinations

# CSV의 여행지 데이터를 Gemini 프롬프트 형식으로 변환
def format_data_for_prompt(df):
    lines = []
    for _, row in df.iterrows():
        # 각 행의 여행지, 제목, 부제목 정보 추출
        place = row.get('여행지', '알 수 없음')
        title = row.get('제목', '')
        subtitle = row.get('부제목', '')
        # 형식화된 문자열로 리스트에 추가
        lines.append(f"장소명: {place}, 제목: {title}, 부제목: {subtitle}")
    # 줄바꿈으로 연결하여 하나의 문자열로 반환
    return "\n".join(lines)

# 사용자 입력을 바탕으로 Gemini API를 통해 여행지 추천 결과 생성
def recommend_travel_places(user_input: str, csv_path: str) -> str:
    # CSV에서 여행지 데이터 로드
    df = load_destinations(csv_path)
    # Gemini 프롬프트용 데이터 요약 문자열 생성
    data_summary = format_data_for_prompt(df)

    # LLM에게 전달할 프롬프트 구성
    prompt = f"""
당신은 부산지역 여행지 추천 전문가입니다.

사용자 입력: "{user_input}"

다음은 여행지 리스트입니다: 
{data_summary}

사용자의 여행 스타일과 조건에 부합하는 모든 적절한 부산 지역 여행지를 제목, 부제목을 활용하여 추천해주세요.  
각 장소에 대해 추천 이유도 함께 설명해주세요.  
추천 개수는 제한하지 말고, 조건에 맞는 곳은 모두 포함해주세요.
"""
    # Gemini 모델에 프롬프트 전달하고 결과 반환
    return ask_gemini(prompt)
