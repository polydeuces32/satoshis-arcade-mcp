import os

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from api.routes import tetris, pingpong, leaderboard
from api.database import db

app = FastAPI(
    title="Satoshi's Arcade MCP",
    description="AI-powered retro arcade with adaptive learning",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Handle serverless (api/static bundled) and local dev (frontend/ at root)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_STATIC = os.path.join(BASE_DIR, "static")
_ROOT_FRONTEND = os.path.join(os.path.dirname(BASE_DIR), "frontend")
FRONTEND_PATH = _STATIC if os.path.exists(os.path.join(_STATIC, "arcade")) else _ROOT_FRONTEND

# Only mount static files if frontend directory exists (may be missing in serverless)
try:
    if os.path.exists(FRONTEND_PATH):
        app.mount("/frontend", StaticFiles(directory=FRONTEND_PATH), name="frontend")
except Exception:
    pass  # Serverless may not have filesystem layout; routes still serve HTML via FileResponse

app.include_router(tetris.router)
app.include_router(pingpong.router)
app.include_router(leaderboard.router)

@app.on_event("startup")
async def startup_event():
    try:
        db.init_database()
    except Exception as e:
        print(f"Database initialization error: {e}")  # noqa: T201

@app.get("/")
def home():
    if os.path.exists(os.path.join(FRONTEND_PATH, "arcade", "index.html")):
        return FileResponse(os.path.join(FRONTEND_PATH, "arcade", "index.html"))
    else:
        return {
            "message": "Satoshi's Arcade MCP API",
            "status": "running",
            "frontend": "not available in serverless mode"
        }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "Satoshi's Arcade MCP is running",
        "games": ["pingpong", "tetris"],
        "version": "1.0.0"
    }
