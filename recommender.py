from gemini_api import ask_gemini
from utils import load_destinations

def format_data_for_prompt(df):
    lines = []
    for _, row in df.iterrows():
        place = row.get('여행지', '알 수 없음')
        title = row.get('제목', '')
        subtitle = row.get('부제목', '')
        lines.append(f"장소명: {place}, 제목: {title}, 부제목: {subtitle}")
    return "\n".join(lines)

def recommend_travel_places(user_input: str, csv_path: str) -> str:
    df = load_destinations(csv_path)
    data_summary = format_data_for_prompt(df)

    prompt = f"""
당신은 부산지역 여행지 추천 전문가입니다.

사용자 입력: "{user_input}"

다음은 여행지 리스트입니다: 
{data_summary}

사용자의 여행 스타일과 조건에 부합하는 모든 적절한 부산 지역 여행지를 제목, 부제목을 활용하여 추천해주세요.  
각 장소에 대해 추천 이유도 함께 설명해주세요.  
추천 개수는 제한하지 말고, 조건에 맞는 곳은 모두 포함해주세요.
"""
    return ask_gemini(prompt)
