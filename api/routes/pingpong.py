import random
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import os
import uuid
from datetime import datetime

from api.ai.difficulty_agent import pingpong_agent
from api.database import db

router = APIRouter(prefix="/pingpong", tags=["Ping Pong"])

# Prefer api/static (Vercel bundle), else frontend/ at project root
_API_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ROOT = os.path.dirname(_API_DIR)
_STATIC_FILE = os.path.join(_API_DIR, "static", "pingpong", "index.html")
_ROOT_FILE = os.path.join(_ROOT, "frontend", "pingpong", "index.html")
FRONTEND_PATH = _STATIC_FILE if os.path.exists(_STATIC_FILE) else _ROOT_FILE

# Game state management
active_sessions = {}

class GameSession(BaseModel):
    session_id: str
    player_id: int
    game_session_id: int
    ai_difficulty: float
    player_score: int = 0
    ai_score: int = 0
    game_state: Dict = {}
    created_at: datetime

class GameAction(BaseModel):
    session_id: str
    action_type: str  # "paddle_move", "ball_hit", "score"
    action_data: Dict
    timestamp: float

class GameOutcome(BaseModel):
    session_id: str
    winner: str  # "player", "ai", "ongoing"
    final_score: Dict
    game_duration: float
    ai_performance: Dict

@router.get("")
def serve_pingpong():
    """Serve the Ping-Pong game frontend"""
    if not os.path.exists(FRONTEND_PATH):
        print("⚠️  Ping-Pong file missing:", FRONTEND_PATH)
        return {"error": "Ping-Pong file not found."}
    return FileResponse(FRONTEND_PATH)

@router.post("/start-session")
def start_game_session():
    """Start a new Ping-Pong game session"""
    session_id = str(uuid.uuid4())
    
    # Create player in database
    player_id = db.create_player(session_id)
    
    # Get AI difficulty settings
    ai_settings = pingpong_agent.get_adaptive_difficulty(session_id, "pingpong")
    
    # Start game session in database
    game_session_id = db.start_game_session(player_id, "pingpong", ai_settings['difficulty_level'])
    
    # Create active session
    session = GameSession(
        session_id=session_id,
        player_id=player_id,
        game_session_id=game_session_id,
        ai_difficulty=ai_settings['difficulty_level'],
        game_state={
            'ball_x': 400,
            'ball_y': 250,
            'ball_speed_x': 5,
            'ball_speed_y': 5,
            'player_y': 200,
            'ai_y': 200,
            'ai_params': ai_settings['behavior_params']
        },
        created_at=datetime.now()
    )
    
    active_sessions[session_id] = session
    
    return {
        "session_id": session_id,
        "ai_difficulty": ai_settings['difficulty_level'],
        "ai_params": ai_settings['behavior_params'],
        "message": "Game session started!"
    }

@router.post("/action")
def process_game_action(action: GameAction):
    """Process a game action and return AI response"""
    if action.session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    session = active_sessions[action.session_id]
    
    # Update game state from client (ball position, paddles) so AI uses current state
    for key in ('ball_x', 'ball_y', 'ball_speed_x', 'ball_speed_y', 'player_y', 'ai_y'):
        if key in action.action_data and action.action_data[key] is not None:
            session.game_state[key] = action.action_data[key]
    if action.action_type == "paddle_move":
        session.game_state['player_y'] = action.action_data.get('y', session.game_state['player_y'])
        
    elif action.action_type == "ball_hit":
        # Record AI feedback for learning
        learning_data = pingpong_agent.learn_from_outcome(
            player_action=f"hit_at_{action.action_data.get('ball_y', 0)}",
            ai_response=f"ai_position_{session.game_state['ai_y']}",
            outcome="ball_hit",
            game_context=session.game_state
        )
        db.record_ai_feedback(
            session.game_session_id,
            "pingpong",
            learning_data.get("player_action", ""),
            learning_data.get("ai_response", ""),
            learning_data.get("outcome", ""),
            learning_data.get("difficulty_level", 0.5),
            learning_data,
        )
        
    elif action.action_type == "score":
        if action.action_data.get('scorer') == 'player':
            session.player_score += 1
        else:
            session.ai_score += 1
    
    # Calculate AI response
    ai_response = calculate_ai_move(session)
    
    return {
        "ai_move": ai_response,
        "game_state": session.game_state,
        "scores": {
            "player": session.player_score,
            "ai": session.ai_score
        }
    }

def calculate_ai_move(session: GameSession) -> Dict:
    """Calculate AI paddle movement based on game state and difficulty"""
    ai_params = session.game_state['ai_params']
    ball_x = session.game_state['ball_x']
    ball_y = session.game_state['ball_y']
    ball_speed_x = session.game_state['ball_speed_x']
    ball_speed_y = session.game_state['ball_speed_y']
    
    # Predict ball trajectory
    if ball_speed_x > 0:  # Ball moving towards AI
        # Calculate where ball will be when it reaches AI paddle
        time_to_paddle = (800 - ball_x) / ball_speed_x
        predicted_y = ball_y + (ball_speed_y * time_to_paddle)
        
        # Apply prediction accuracy based on difficulty
        prediction_accuracy = ai_params['prediction_accuracy']
        if random.random() > prediction_accuracy:
            # Add some randomness to make it less perfect
            predicted_y += random.gauss(0, 50)
        
        # Clamp prediction to canvas bounds (canvas height 500, paddle height 100 → ai_y in [0, 400])
        predicted_y = max(50, min(400, predicted_y))
        
        # Move AI paddle towards predicted position
        current_ai_y = session.game_state['ai_y']
        paddle_speed = ai_params['paddle_speed']
        
        if abs(predicted_y - current_ai_y) > 5:
            if predicted_y > current_ai_y:
                new_ai_y = min(current_ai_y + paddle_speed, 400)
            else:
                new_ai_y = max(current_ai_y - paddle_speed, 0)
        else:
            new_ai_y = current_ai_y
            
    else:  # Ball moving away from AI
        # Move towards center (canvas 800x500 → center y = 250)
        current_ai_y = session.game_state['ai_y']
        center_y = 250
        paddle_speed = ai_params['paddle_speed'] * 0.5  # Slower when ball is away
        
        if abs(center_y - current_ai_y) > 10:
            if center_y > current_ai_y:
                new_ai_y = min(current_ai_y + paddle_speed, 400)
            else:
                new_ai_y = max(current_ai_y - paddle_speed, 0)
        else:
            new_ai_y = current_ai_y
    
    session.game_state['ai_y'] = new_ai_y
    
    return {
        'ai_y': new_ai_y,
        'difficulty': session.ai_difficulty,
        'prediction_accuracy': ai_params['prediction_accuracy']
    }

@router.post("/end-session")
def end_game_session(outcome: GameOutcome):
    """End a game session and record results"""
    if outcome.session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    session = active_sessions[outcome.session_id]
    
    # End session in database
    final_score = outcome.final_score.get('player', 0)
    db.end_game_session(session.game_session_id, final_score)
    
    # Update leaderboard if player won
    if outcome.winner == "player" and final_score > 0:
        db.update_leaderboard(
            session.player_id, 
            "pingpong", 
            final_score, 
            session.ai_difficulty, 
            session.game_session_id
        )
    
    # Record final AI learning data
    learning_data = pingpong_agent.learn_from_outcome(
        player_action="game_end",
        ai_response="final_position",
        outcome=outcome.winner,
        game_context={
            'final_score': outcome.final_score,
            'game_duration': outcome.game_duration,
            'ai_performance': outcome.ai_performance
        }
    )
    
    db.record_ai_feedback(
        session.game_session_id,
        "pingpong",
        learning_data.get("player_action", ""),
        learning_data.get("ai_response", ""),
        learning_data.get("outcome", ""),
        learning_data.get("difficulty_level", 0.5),
        learning_data,
    )

    # Remove from active sessions
    del active_sessions[outcome.session_id]

    return {
        "message": "Game session ended",
        "final_score": outcome.final_score,
        "ai_difficulty": session.ai_difficulty
    }

@router.get("/leaderboard")
def get_pingpong_leaderboard():
    """Get Ping-Pong leaderboard"""
    leaderboard = db.get_leaderboard("pingpong", 10)
    return {
        "game_type": "pingpong",
        "leaderboard": leaderboard,
        "total_entries": len(leaderboard)
    }

@router.get("/ai-stats")
def get_ai_stats():
    """Get AI performance statistics"""
    metrics = db.get_ai_metrics("pingpong")
    return {
        "game_type": "pingpong",
        "ai_metrics": metrics,
        "current_difficulty": pingpong_agent.difficulty_level,
        "performance_history": pingpong_agent.ai_performance_history[-10:] if pingpong_agent.ai_performance_history else []
    }

print("✅ Enhanced Ping-Pong route loaded with AI integration")
