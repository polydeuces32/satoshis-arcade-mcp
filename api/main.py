from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from api.routes import tetris, pingpong, leaderboard
import os

app = FastAPI(
    title="Satoshi's Arcade MCP",
    description="An AI-powered arcade that learns from every move",
    version="1.0.0"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_PATH = os.path.join(os.path.dirname(BASE_DIR), "frontend")

# Mount static files
app.mount("/frontend", StaticFiles(directory=FRONTEND_PATH), name="frontend")

# Include API routes
app.include_router(tetris.router)
app.include_router(pingpong.router)
app.include_router(leaderboard.router)

@app.get("/")
def home():
    """Serve the main arcade menu"""
    return FileResponse(os.path.join(FRONTEND_PATH, "arcade", "index.html"))

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Satoshi's Arcade MCP is running",
        "version": "1.0.0",
        "games": ["pingpong", "tetris"],
        "features": ["ai_learning", "leaderboard", "pwa_support"]
    }

@app.get("/api/stats")
def get_arcade_stats():
    """Get overall arcade statistics"""
    try:
        # Import database here to avoid circular imports
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from database import db
        
        # Get basic stats
        pingpong_leaderboard = db.get_leaderboard("pingpong", 5)
        tetris_leaderboard = db.get_leaderboard("tetris", 5)
        
        return {
            "arcade_stats": {
                "total_games": len(pingpong_leaderboard) + len(tetris_leaderboard),
                "pingpong_players": len(pingpong_leaderboard),
                "tetris_players": len(tetris_leaderboard),
                "ai_learning_active": True,
                "features_enabled": [
                    "adaptive_difficulty",
                    "player_analytics", 
                    "ai_performance_tracking",
                    "pwa_support",
                    "neon_bauhaus_ui"
                ]
            },
            "message": "Arcade statistics retrieved successfully"
        }
        
    except Exception as e:
        return {
            "arcade_stats": {
                "total_games": 0,
                "pingpong_players": 0,
                "tetris_players": 0,
                "ai_learning_active": False,
                "error": str(e)
            }
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
