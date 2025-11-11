import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

class Config:
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY가 .env 파일에 설정되지 않았습니다.")

    # CSV 경로를 환경변수로도 주입 가능 (fallback은 기존 프로젝트 내부 경로)
    DATA_CSV_PATH = os.getenv('DATA_CSV_PATH', str(BASE_DIR / 'backend' / 'data' / 'busan_data.csv'))
