from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import os
import uuid
from datetime import datetime

# Import our AI agent and database
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ai.difficulty_agent import tetris_agent
from database import db

router = APIRouter(prefix="/tetris", tags=["Tetris"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
FRONTEND_PATH = os.path.join(BASE_DIR, "frontend", "tetris", "index.html")

# Game state management
active_sessions = {}

class TetrisSession(BaseModel):
    session_id: str
    player_id: int
    game_session_id: int
    ai_difficulty: float
    score: int = 0
    level: int = 1
    lines_cleared: int = 0
    game_state: Dict = {}
    created_at: datetime

class TetrisAction(BaseModel):
    session_id: str
    action_type: str  # "move", "rotate", "hard_drop", "piece_placed", "lines_cleared", "game_over"
    action_data: Dict
    timestamp: float

class TetrisOutcome(BaseModel):
    session_id: str
    final_score: int
    level_reached: int
    lines_cleared: int
    game_duration: float
    ai_performance: Dict

@router.get("")
def serve_tetris():
    """Serve the Tetris game frontend"""
    if not os.path.exists(FRONTEND_PATH):
        print("⚠️  Tetris file missing:", FRONTEND_PATH)
        return {"error": "Tetris file not found."}
    return FileResponse(FRONTEND_PATH)

@router.post("/start-session")
def start_tetris_session():
    """Start a new Tetris game session"""
    session_id = str(uuid.uuid4())
    
    # Create player in database
    player_id = db.create_player(session_id)
    
    # Get AI difficulty settings
    ai_settings = tetris_agent.get_adaptive_difficulty(session_id, "tetris")
    
    # Start game session in database
    game_session_id = db.start_game_session(player_id, "tetris", ai_settings['difficulty_level'])
    
    # Create active session
    session = TetrisSession(
        session_id=session_id,
        player_id=player_id,
        game_session_id=game_session_id,
        ai_difficulty=ai_settings['difficulty_level'],
        game_state={
            'board_width': 10,
            'board_height': 20,
            'ai_params': ai_settings['behavior_params']
        },
        created_at=datetime.now()
    )
    
    active_sessions[session_id] = session
    
    return {
        "session_id": session_id,
        "ai_difficulty": ai_settings['difficulty_level'],
        "ai_params": ai_settings['behavior_params'],
        "message": "Tetris session started!"
    }

@router.post("/action")
def process_tetris_action(action: TetrisAction):
    """Process a Tetris game action and return AI response"""
    if action.session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Tetris session not found")
    
    session = active_sessions[action.session_id]
    
    # Update game state based on action
    if action.action_type == "move":
        direction = action.action_data.get('direction', '')
        # Record player movement for AI learning
        learning_data = tetris_agent.learn_from_outcome(
            player_action=f"move_{direction}",
            ai_response="observe",
            outcome="move_recorded",
            game_context={
                'score': session.score,
                'level': session.level,
                'lines': session.lines_cleared
            }
        )
        
    elif action.action_type == "rotate":
        learning_data = tetris_agent.learn_from_outcome(
            player_action="rotate",
            ai_response="observe",
            outcome="rotation_recorded",
            game_context={
                'score': session.score,
                'level': session.level,
                'lines': session.lines_cleared
            }
        )
        
    elif action.action_type == "hard_drop":
        learning_data = tetris_agent.learn_from_outcome(
            player_action="hard_drop",
            ai_response="observe",
            outcome="drop_recorded",
            game_context={
                'score': session.score,
                'level': session.level,
                'lines': session.lines_cleared
            }
        )
        
    elif action.action_type == "piece_placed":
        # Update session score
        session.score = action.action_data.get('score', session.score)
        
        learning_data = tetris_agent.learn_from_outcome(
            player_action="piece_placed",
            ai_response="analyze_placement",
            outcome="placement_recorded",
            game_context={
                'score': session.score,
                'level': session.level,
                'lines': session.lines_cleared,
                'piece_type': action.action_data.get('piece_type'),
                'position': action.action_data.get('position')
            }
        )
        
    elif action.action_type == "lines_cleared":
        session.lines_cleared = action.action_data.get('lines', 0)
        session.level = action.action_data.get('level', session.level)
        session.score = action.action_data.get('score', session.score)
        
        learning_data = tetris_agent.learn_from_outcome(
            player_action="lines_cleared",
            ai_response="analyze_efficiency",
            outcome="efficiency_recorded",
            game_context={
                'score': session.score,
                'level': session.level,
                'lines': session.lines_cleared,
                'lines_cleared': action.action_data.get('lines', 0)
            }
        )
        
    elif action.action_type == "game_over":
        session.score = action.action_data.get('final_score', session.score)
        session.level = action.action_data.get('level', session.level)
        session.lines_cleared = action.action_data.get('lines', session.lines_cleared)
        
        learning_data = tetris_agent.learn_from_outcome(
            player_action="game_over",
            ai_response="analyze_performance",
            outcome="game_completed",
            game_context={
                'final_score': session.score,
                'level_reached': session.level,
                'lines_cleared': session.lines_cleared
            }
        )
    
    # Save learning data
    tetris_agent.save_learning_data(learning_data)
    
    return {
        "ai_response": "action_recorded",
        "game_state": {
            "score": session.score,
            "level": session.level,
            "lines": session.lines_cleared,
            "ai_difficulty": session.ai_difficulty
        }
    }

@router.post("/end-session")
def end_tetris_session(outcome: TetrisOutcome):
    """End a Tetris game session and record results"""
    if outcome.session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Tetris session not found")
    
    session = active_sessions[outcome.session_id]
    
    # End session in database
    db.end_game_session(session.game_session_id, outcome.final_score)
    
    # Update leaderboard if score is good
    if outcome.final_score > 0:
        db.update_leaderboard(
            session.player_id, 
            "tetris", 
            outcome.final_score, 
            session.ai_difficulty, 
            session.game_session_id
        )
    
    # Record final AI learning data
    learning_data = tetris_agent.learn_from_outcome(
        player_action="session_end",
        ai_response="final_analysis",
        outcome="session_completed",
        game_context={
            'final_score': outcome.final_score,
            'level_reached': outcome.level_reached,
            'lines_cleared': outcome.lines_cleared,
            'game_duration': outcome.game_duration,
            'ai_performance': outcome.ai_performance
        }
    )
    
    tetris_agent.save_learning_data(learning_data)
    
    # Remove from active sessions
    del active_sessions[outcome.session_id]
    
    return {
        "message": "Tetris session ended",
        "final_score": outcome.final_score,
        "level_reached": outcome.level_reached,
        "lines_cleared": outcome.lines_cleared,
        "ai_difficulty": session.ai_difficulty
    }

@router.get("/leaderboard")
def get_tetris_leaderboard():
    """Get Tetris leaderboard"""
    leaderboard = db.get_leaderboard("tetris", 10)
    return {
        "game_type": "tetris",
        "leaderboard": leaderboard,
        "total_entries": len(leaderboard)
    }

@router.get("/ai-stats")
def get_tetris_ai_stats():
    """Get Tetris AI performance statistics"""
    metrics = db.get_ai_metrics("tetris")
    return {
        "game_type": "tetris",
        "ai_metrics": metrics,
        "current_difficulty": tetris_agent.difficulty_level,
        "performance_history": tetris_agent.ai_performance_history[-10:] if tetris_agent.ai_performance_history else []
    }

@router.get("/ai-suggestions")
def get_ai_suggestions(session_id: str):
    """Get AI suggestions for optimal piece placement"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Tetris session not found")
    
    session = active_sessions[session_id]
    
    # Simple AI suggestions based on current game state
    suggestions = {
        "placement_hints": [
            "Try to create horizontal lines",
            "Keep the board balanced",
            "Save I-pieces for Tetris clears"
        ],
        "difficulty_adjustment": session.ai_difficulty,
        "efficiency_score": min(100, session.score / max(1, session.lines_cleared))
    }
    
    return suggestions

print("✅ Enhanced Tetris route loaded with AI integration")
