import json
import statistics
from typing import Dict, List, Tuple
from datetime import datetime
import sqlite3
import os


def _mean(x: List[float]) -> float:
    return sum(x) / len(x) if x else 0.0


def _variance(x: List[float]) -> float:
    try:
        return statistics.variance(x) if len(x) > 1 else 0.0
    except statistics.StatisticsError:
        return 0.0


def _clip(x: float, a: float, b: float) -> float:
    return max(a, min(b, x))


def _interp(x: float, xp: List[float], fp: List[float]) -> float:
    if x <= xp[0]:
        return fp[0]
    if x >= xp[-1]:
        return fp[-1]
    for i in range(len(xp) - 1):
        if xp[i] <= x <= xp[i + 1]:
            t = (x - xp[i]) / (xp[i + 1] - xp[i]) if xp[i + 1] != xp[i] else 0
            return fp[i] + t * (fp[i + 1] - fp[i])
    return fp[-1]

class DifficultyAgent:
    """
    AI Agent that learns and adapts difficulty based on player performance.
    Uses reinforcement learning principles to optimize gameplay experience.
    """

    def __init__(self, game_type: str = "pingpong"):
        self.game_type = game_type
        self.difficulty_level = 0.5
        self.learning_rate = 0.01
        self.memory_size = 100
        self.player_performance_history = []
        self.ai_performance_history = []
        self.game_params = self._get_game_params()

    def _get_game_params(self) -> Dict:
        if self.game_type == "pingpong":
            return {
                'reaction_time_range': (0.1, 0.8),
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
        if not recent_performance:
            return self.difficulty_level
        win_rate = _mean(recent_performance)
        performance_variance = _variance(recent_performance)
        if win_rate > 0.7:
            difficulty_adjustment = 0.1
        elif win_rate < 0.3:
            difficulty_adjustment = -0.1
        else:
            difficulty_adjustment = 0.02 if performance_variance > 0.1 else -0.02
        new_difficulty = self.difficulty_level + (difficulty_adjustment * self.learning_rate)
        self.difficulty_level = _clip(new_difficulty, 0.0, 1.0)
        return self.difficulty_level

    def get_ai_behavior_params(self, difficulty: float) -> Dict:
        params = {}
        if self.game_type == "pingpong":
            reaction_time = _interp(difficulty, [0, 1],
                                   [self.game_params['reaction_time_range'][1],
                                    self.game_params['reaction_time_range'][0]])
            prediction_accuracy = _interp(difficulty, [0, 1],
                                          [self.game_params['prediction_accuracy_range'][0],
                                           self.game_params['prediction_accuracy_range'][1]])
            paddle_speed = _interp(difficulty, [0, 1],
                                  [self.game_params['paddle_speed_range'][0],
                                   self.game_params['paddle_speed_range'][1]])
            params = {
                'reaction_time': reaction_time,
                'prediction_accuracy': prediction_accuracy,
                'paddle_speed': paddle_speed,
                'ball_speed_modifier': 1.0 + (difficulty - 0.5) * 0.4
            }
        elif self.game_type == "tetris":
            drop_speed = _interp(difficulty, [0, 1],
                                [self.game_params['drop_speed_range'][0],
                                 self.game_params['drop_speed_range'][1]])
            rotation_delay = _interp(difficulty, [0, 1],
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
        learning_data = {
            'timestamp': datetime.now().isoformat(),
            'player_action': player_action,
            'ai_response': ai_response,
            'outcome': outcome,
            'difficulty_level': self.difficulty_level,
            'game_context': game_context
        }
        if outcome == "ai_win":
            self.ai_performance_history.append(1.0)
        elif outcome == "player_win":
            self.ai_performance_history.append(0.0)
        else:
            self.ai_performance_history.append(0.5)
        if len(self.ai_performance_history) > self.memory_size:
            self.ai_performance_history.pop(0)
        if len(self.ai_performance_history) >= 10:
            recent_performance = self.ai_performance_history[-10:]
            self.calculate_difficulty({}, recent_performance)
        return learning_data

    def predict_player_move(self, game_state: Dict) -> str:
        if not self.player_performance_history:
            return "center"
        recent_moves = self.player_performance_history[-5:] if len(self.player_performance_history) >= 5 else self.player_performance_history
        if len(recent_moves) >= 3 and recent_moves[-1] == recent_moves[-3]:
            return recent_moves[-1]
        return "center"

    def get_adaptive_difficulty(self, session_id: str, game_type: str) -> Dict:
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

pingpong_agent = DifficultyAgent("pingpong")
tetris_agent = DifficultyAgent("tetris")
