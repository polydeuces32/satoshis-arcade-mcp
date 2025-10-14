import numpy as np
import json
from typing import Dict, List, Tuple
from datetime import datetime
import sqlite3
import os

class DifficultyAgent:
    """
    AI Agent that learns and adapts difficulty based on player performance.
    Uses reinforcement learning principles to optimize gameplay experience.
    """
    
    def __init__(self, game_type: str = "pingpong"):
        self.game_type = game_type
        self.difficulty_level = 0.5  # Start at medium difficulty
        self.learning_rate = 0.01
        self.memory_size = 100
        self.player_performance_history = []
        self.ai_performance_history = []
        
        # Game-specific parameters
        self.game_params = self._get_game_params()
        
    def _get_game_params(self) -> Dict:
        """Get game-specific parameters for AI behavior"""
        if self.game_type == "pingpong":
            return {
                'reaction_time_range': (0.1, 0.8),  # seconds
                'prediction_accuracy_range': (0.3, 0.95),
                'paddle_speed_range': (2, 8),
                'ball_speed_modifier_range': (0.8, 1.2)
            }
        elif self.game_type == "tetris":
            return {
                'drop_speed_range': (0.5, 2.0),
                'rotation_delay_range': (0.1, 0.5),
                'line_clear_bonus_range': (1.0, 2.0)
            }
        else:
            return {}
    
    def calculate_difficulty(self, player_stats: Dict, recent_performance: List[float]) -> float:
        """
        Calculate optimal difficulty based on player performance.
        Returns difficulty level between 0.0 (easy) and 1.0 (hard).
        """
        if not recent_performance:
            return self.difficulty_level
        
        # Calculate player win rate over recent games
        win_rate = np.mean(recent_performance)
        
        # Calculate performance variance (consistency)
        performance_variance = np.var(recent_performance)
        
        # Adaptive difficulty adjustment
        if win_rate > 0.7:  # Player winning too much
            difficulty_adjustment = 0.1
        elif win_rate < 0.3:  # Player losing too much
            difficulty_adjustment = -0.1
        else:  # Balanced performance
            difficulty_adjustment = 0.02 if performance_variance > 0.1 else -0.02
        
        # Apply learning rate and bounds
        new_difficulty = self.difficulty_level + (difficulty_adjustment * self.learning_rate)
        self.difficulty_level = np.clip(new_difficulty, 0.0, 1.0)
        
        return self.difficulty_level
    
    def get_ai_behavior_params(self, difficulty: float) -> Dict:
        """Get AI behavior parameters based on difficulty level"""
        params = {}
        
        if self.game_type == "pingpong":
            # Map difficulty to reaction time (higher difficulty = faster reaction)
            reaction_time = np.interp(difficulty, [0, 1], 
                                    [self.game_params['reaction_time_range'][1], 
                                     self.game_params['reaction_time_range'][0]])
            
            # Map difficulty to prediction accuracy
            prediction_accuracy = np.interp(difficulty, [0, 1], 
                                           [self.game_params['prediction_accuracy_range'][0], 
                                            self.game_params['prediction_accuracy_range'][1]])
            
            # Map difficulty to paddle speed
            paddle_speed = np.interp(difficulty, [0, 1], 
                                   [self.game_params['paddle_speed_range'][0], 
                                    self.game_params['paddle_speed_range'][1]])
            
            params = {
                'reaction_time': reaction_time,
                'prediction_accuracy': prediction_accuracy,
                'paddle_speed': paddle_speed,
                'ball_speed_modifier': 1.0 + (difficulty - 0.5) * 0.4
            }
            
        elif self.game_type == "tetris":
            # Map difficulty to drop speed and rotation delay
            drop_speed = np.interp(difficulty, [0, 1], 
                                 [self.game_params['drop_speed_range'][0], 
                                  self.game_params['drop_speed_range'][1]])
            
            rotation_delay = np.interp(difficulty, [0, 1], 
                                     [self.game_params['rotation_delay_range'][1], 
                                      self.game_params['rotation_delay_range'][0]])
            
            params = {
                'drop_speed': drop_speed,
                'rotation_delay': rotation_delay,
                'line_clear_bonus': 1.0 + difficulty * 0.5
            }
        
        return params
    
    def learn_from_outcome(self, player_action: str, ai_response: str, 
                          outcome: str, game_context: Dict):
        """Learn from game outcome and update AI behavior"""
        
        # Record the interaction
        learning_data = {
            'timestamp': datetime.now().isoformat(),
            'player_action': player_action,
            'ai_response': ai_response,
            'outcome': outcome,
            'difficulty_level': self.difficulty_level,
            'game_context': game_context
        }
        
        # Update performance history
        if outcome == "ai_win":
            self.ai_performance_history.append(1.0)
        elif outcome == "player_win":
            self.ai_performance_history.append(0.0)
        else:
            self.ai_performance_history.append(0.5)  # Draw/tie
        
        # Keep memory size manageable
        if len(self.ai_performance_history) > self.memory_size:
            self.ai_performance_history.pop(0)
        
        # Update difficulty based on recent performance
        if len(self.ai_performance_history) >= 10:
            recent_performance = self.ai_performance_history[-10:]
            self.calculate_difficulty({}, recent_performance)
        
        return learning_data
    
    def predict_player_move(self, game_state: Dict) -> str:
        """Predict player's next move based on game state and history"""
        if not self.player_performance_history:
            return "center"  # Default prediction
        
        # Simple pattern recognition for player behavior
        recent_moves = self.player_performance_history[-5:] if len(self.player_performance_history) >= 5 else self.player_performance_history
        
        # Analyze patterns (this is a simplified version)
        if len(recent_moves) >= 3:
            # Look for repetitive patterns
            if recent_moves[-1] == recent_moves[-3]:
                return recent_moves[-1]  # Predict repetition
        
        return "center"  # Default to center prediction
    
    def get_adaptive_difficulty(self, session_id: str, game_type: str) -> Dict:
        """Get adaptive difficulty settings for a game session"""
        # This would typically query the database for player history
        # For now, return current difficulty settings
        
        difficulty = self.difficulty_level
        behavior_params = self.get_ai_behavior_params(difficulty)
        
        return {
            'difficulty_level': difficulty,
            'behavior_params': behavior_params,
            'session_id': session_id,
            'game_type': game_type,
            'timestamp': datetime.now().isoformat()
        }
    
    def save_learning_data(self, learning_data: Dict, db_path: str = "db.sqlite"):
        """Save learning data to database"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO ai_feedback 
                (game_type, player_action, ai_response, outcome, 
                 difficulty_level, learning_data, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.game_type,
                learning_data.get('player_action', ''),
                learning_data.get('ai_response', ''),
                learning_data.get('outcome', ''),
                learning_data.get('difficulty_level', 0.5),
                json.dumps(learning_data),
                learning_data.get('timestamp', datetime.now().isoformat())
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving learning data: {e}")
            return False

# Global AI agent instances
pingpong_agent = DifficultyAgent("pingpong")
tetris_agent = DifficultyAgent("tetris")
