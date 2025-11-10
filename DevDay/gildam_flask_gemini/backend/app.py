from flask import Flask, send_from_directory
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
FRONT = BASE / "frontend"
PAGES = FRONT / "pages"
STATIC_DIR = FRONT / "static"

app = Flask(__name__, static_folder=None)  # 기본 static 비활성화(우리가 직접 라우팅)

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

from flask import Flask, send_from_directory
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
FRONT = BASE / "frontend"
PAGES = FRONT / "pages"
STATIC_DIR = FRONT / "static"

app = Flask(__name__, static_folder=None)  # 기본 static 비활성화(우리가 직접 라우팅)

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



# 필요시 다른 페이지도 위와 같이 추가...
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
