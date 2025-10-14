from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from api.routes import tetris, pingpong, leaderboard
import os
from database import db

app = FastAPI(
    title="Satoshi's Arcade MCP",
    description="AI-powered retro arcade with adaptive learning",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_PATH = os.path.join(os.path.dirname(BASE_DIR), "frontend")

app.mount("/frontend", StaticFiles(directory=FRONTEND_PATH), name="frontend")

app.include_router(tetris.router)
app.include_router(pingpong.router)
app.include_router(leaderboard.router)

@app.on_event("startup")
async def startup_event():
    db.init_database()
    print("Database initialized successfully")

@app.get("/")
def home():
    return FileResponse(os.path.join(FRONTEND_PATH, "arcade", "index.html"))

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "Satoshi's Arcade MCP is running",
        "games": ["pingpong", "tetris"],
        "version": "1.0.0"
    }
