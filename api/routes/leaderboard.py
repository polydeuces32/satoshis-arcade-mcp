from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from typing import Dict, List, Optional
import os
import json

from api.database import db

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])

@router.get("")
def get_global_leaderboard():
    """Get global leaderboard across all games"""
    try:
        # Get leaderboards for each game type
        pingpong_leaderboard = db.get_leaderboard("pingpong", 5)
        tetris_leaderboard = db.get_leaderboard("tetris", 5)
        
        # Combine and format results
        global_leaderboard = {
            "pingpong": {
                "game_name": "Ping-Pong AI",
                "emoji": "🏓",
                "top_scores": pingpong_leaderboard,
                "total_players": len(pingpong_leaderboard)
            },
            "tetris": {
                "game_name": "Tetris AI",
                "emoji": "🧱",
                "top_scores": tetris_leaderboard,
                "total_players": len(tetris_leaderboard)
            }
        }
        
        return {
            "message": "Global leaderboard retrieved successfully",
            "leaderboard": global_leaderboard,
            "last_updated": "2025-01-14T16:00:00Z"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve leaderboard: {str(e)}")

@router.get("/pingpong")
def get_pingpong_leaderboard():
    """Get Ping-Pong specific leaderboard"""
    try:
        leaderboard = db.get_leaderboard("pingpong", 20)
        
        return {
            "game_type": "pingpong",
            "game_name": "Ping-Pong AI",
            "leaderboard": leaderboard,
            "total_entries": len(leaderboard),
            "description": "Top Ping-Pong scores against AI opponents"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve Ping-Pong leaderboard: {str(e)}")

@router.get("/tetris")
def get_tetris_leaderboard():
    """Get Tetris specific leaderboard"""
    try:
        leaderboard = db.get_leaderboard("tetris", 20)
        
        return {
            "game_type": "tetris",
            "game_name": "Tetris AI",
            "leaderboard": leaderboard,
            "total_entries": len(leaderboard),
            "description": "Top Tetris scores with AI difficulty scaling"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve Tetris leaderboard: {str(e)}")

@router.get("/player/{session_id}")
def get_player_stats(session_id: str):
    """Get statistics for a specific player"""
    try:
        stats = db.get_player_stats(session_id)
        
        if not stats:
            raise HTTPException(status_code=404, detail="Player not found")
        
        return {
            "session_id": session_id,
            "stats": stats,
            "message": "Player statistics retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve player stats: {str(e)}")

@router.get("/ai-performance")
def get_ai_performance_stats():
    """Get AI performance statistics across all games"""
    try:
        pingpong_metrics = db.get_ai_metrics("pingpong")
        tetris_metrics = db.get_ai_metrics("tetris")
        
        return {
            "ai_performance": {
                "pingpong": {
                    "game_name": "Ping-Pong AI",
                    "metrics": pingpong_metrics,
                    "description": "AI opponent performance metrics"
                },
                "tetris": {
                    "game_name": "Tetris AI", 
                    "metrics": tetris_metrics,
                    "description": "AI difficulty scaling metrics"
                }
            },
            "summary": {
                "total_games_tracked": len(pingpong_metrics) + len(tetris_metrics),
                "ai_learning_active": True,
                "last_updated": "2025-01-14T16:00:00Z"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve AI performance stats: {str(e)}")

@router.get("/rankings")
def get_player_rankings():
    """Get player rankings across all games"""
    try:
        # Get top players from each game
        pingpong_top = db.get_leaderboard("pingpong", 10)
        tetris_top = db.get_leaderboard("tetris", 10)
        
        # Create combined rankings
        player_rankings = {}
        
        # Process Ping-Pong rankings
        for i, entry in enumerate(pingpong_top):
            session_id = entry['session_id']
            if session_id not in player_rankings:
                player_rankings[session_id] = {
                    'session_id': session_id,
                    'games': {},
                    'total_score': 0,
                    'games_played': 0
                }
            
            player_rankings[session_id]['games']['pingpong'] = {
                'score': entry['score'],
                'difficulty': entry['difficulty'],
                'rank': i + 1,
                'achieved_at': entry['achieved_at']
            }
            player_rankings[session_id]['total_score'] += entry['score']
            player_rankings[session_id]['games_played'] += 1
        
        # Process Tetris rankings
        for i, entry in enumerate(tetris_top):
            session_id = entry['session_id']
            if session_id not in player_rankings:
                player_rankings[session_id] = {
                    'session_id': session_id,
                    'games': {},
                    'total_score': 0,
                    'games_played': 0
                }
            
            player_rankings[session_id]['games']['tetris'] = {
                'score': entry['score'],
                'difficulty': entry['difficulty'],
                'rank': i + 1,
                'achieved_at': entry['achieved_at']
            }
            player_rankings[session_id]['total_score'] += entry['score']
            player_rankings[session_id]['games_played'] += 1
        
        # Sort by total score
        sorted_rankings = sorted(
            player_rankings.values(),
            key=lambda x: x['total_score'],
            reverse=True
        )
        
        return {
            "player_rankings": sorted_rankings[:20],  # Top 20 players
            "total_players": len(sorted_rankings),
            "description": "Combined player rankings across all games"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve player rankings: {str(e)}")

print("✅ Enhanced Leaderboard route loaded with comprehensive stats")
