from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from pathlib import Path
import sys
import traceback
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 프로젝트 루트 경로 설정
BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

# ✅ services 폴더에서 임포트
from backend.services.gemini_service import GeminiService
from backend.services.route_optimizer import RouteOptimizer

FRONT = BASE / "frontend"
PAGES = FRONT / "pages"
STATIC_DIR = FRONT / "static"

app = Flask(__name__, static_folder=None)
CORS(app)

# Flask 로그 레벨 설정
app.logger.setLevel(logging.DEBUG)

gemini_service = GeminiService()
route_optimizer = RouteOptimizer()

# --- 정적 파일 ---
@app.route("/static/<path:path>")
def static_files(path):
    return send_from_directory(STATIC_DIR, path)

# --- 페이지 ---
@app.get("/")
def home():
    return send_from_directory(PAGES, "home.html")

@app.get("/dates")
def dates():
    return send_from_directory(PAGES, "dates.html")

@app.get("/purpose")
def purpose():
    return send_from_directory(PAGES, "purpose.html")

@app.get("/theme")
def theme():
    return send_from_directory(PAGES, "theme.html")

@app.get("/itinerary")
def itinerary():
    return send_from_directory(PAGES, "itinerary.html")

# --- API 엔드포인트 ---
@app.post("/api/generate-itinerary")
def generate_itinerary():
    """일정 생성 API"""
    logger.info("="*60)
    logger.info("🚀 일정 생성 API 호출됨")
    logger.info("="*60)
    
    try:
        data = request.get_json()
        logger.info(f"📥 받은 데이터: {data}")
        
        # 입력 검증
        required_fields = ['start', 'end', 'days', 'purpose', 'emotions', 'themes']
        missing = [field for field in required_fields if field not in data]
        
        if missing:
            logger.error(f"필수 필드 누락: {missing}")
            return jsonify({"error": f"필수 필드 누락: {', '.join(missing)}"}), 400
        
        logger.info(f"입력 검증 완료")
        logger.info(f"   - 기간: {data['start']} ~ {data['end']} ({data['days']}일)")
        logger.info(f"   - 목적: {data['purpose']}")
        logger.info(f"   - 감정: {data['emotions']}")
        logger.info(f"   - 테마: {data['themes']}")
        
        # Gemini로 일정 생성
        logger.info("Gemini 일정 생성 시작...")
        result = gemini_service.generate_itinerary(data)
        
        if not result:
            logger.error("일정 생성 실패 (result is None)")
            return jsonify({"error": "일정 생성 실패"}), 500
        
        logger.info("Gemini 일정 생성 완료")
        
        # 각 일차별로 경로 최적화
        logger.info("경로 최적화 시작...")
        for i, day_plan in enumerate(result['itinerary'], 1):
            logger.info(f"   - {i}일차 최적화 중...")
            places = day_plan['places']
            
            # 시간 + 동선 최적화
            optimized = route_optimizer.optimize_route_with_time(places)
            
            # 이동 시간 계산
            optimized = route_optimizer.add_travel_times(optimized)
            
            day_plan['places'] = optimized
            logger.info(f"   - {i}일차 완료: {len(optimized)}개 장소")
        
        logger.info("="*60)
        logger.info(f"최종 일정 생성 완료: {len(result['itinerary'])}일")
        logger.info("="*60)
        
        return jsonify(result)
    
    except Exception as e:
        logger.error("="*60)
        logger.error("치명적 오류 발생:")
        logger.error(f"   오류 타입: {type(e).__name__}")
        logger.error(f"   오류 메시지: {str(e)}")
        logger.error("   전체 스택 트레이스:")
        traceback.print_exc()
        logger.error("="*60)
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(e):
    logger.warning(f"404 Not Found: {request.url}")
    return jsonify({"error": "Not Found"}), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"500 Internal Server Error: {str(e)}")
    traceback.print_exc()
    return jsonify({"error": "Internal Server Error"}), 500

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 GILDAM 서버 시작")
    print("📍 http://127.0.0.1:8000")
    print("🔍 디버그 모드: 활성화")
    print("=" * 60)
    app.run(host="127.0.0.1", port=8000, debug=True, use_reloader=True)
