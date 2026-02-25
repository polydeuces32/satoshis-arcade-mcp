import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
import os

class ArcadeDatabase:
    def __init__(self, db_path: str = None):
        # Use temporary directory for Vercel serverless environment
        if db_path is None:
            import tempfile
            self.db_path = os.path.join(tempfile.gettempdir(), "arcade.db")
        else:
            self.db_path = db_path
        # Defer init to startup so import never fails in serverless
        self._inited = False

    def init_database(self):
        """Initialize the database with required tables"""
        if self._inited:
            return
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_games INTEGER DEFAULT 0,
                total_score INTEGER DEFAULT 0
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER,
                game_type TEXT NOT NULL,
                session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                session_end TIMESTAMP,
                final_score INTEGER DEFAULT 0,
                ai_difficulty REAL DEFAULT 0.5,
                FOREIGN KEY (player_id) REFERENCES players (id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                game_type TEXT NOT NULL,
                player_action TEXT,
                ai_response TEXT,
                outcome TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                difficulty_level REAL,
                learning_data TEXT,
                FOREIGN KEY (session_id) REFERENCES game_sessions (id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leaderboard (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER,
                game_type TEXT NOT NULL,
                score INTEGER NOT NULL,
                difficulty REAL NOT NULL,
                achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                session_id INTEGER,
                FOREIGN KEY (player_id) REFERENCES players (id),
                FOREIGN KEY (session_id) REFERENCES game_sessions (id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_type TEXT NOT NULL,
                difficulty_level REAL NOT NULL,
                win_rate REAL NOT NULL,
                avg_game_duration REAL,
                total_games INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()
        self._inited = True

    def create_player(self, session_id: str) -> int:
        self.init_database()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM players WHERE session_id = ?', (session_id,))
        row = cursor.fetchone()
        if row:
            conn.close()
            return row[0]
        cursor.execute('''
            INSERT INTO players (session_id, last_played)
            VALUES (?, CURRENT_TIMESTAMP)
        ''', (session_id,))
        player_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return player_id

    def start_game_session(self, player_id: int, game_type: str, ai_difficulty: float = 0.5) -> int:
        self.init_database()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO game_sessions (player_id, game_type, ai_difficulty)
            VALUES (?, ?, ?)
        ''', (player_id, game_type, ai_difficulty))
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return session_id

    def end_game_session(self, session_id: int, final_score: int):
        self.init_database()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE game_sessions 
            SET session_end = CURRENT_TIMESTAMP, final_score = ?
            WHERE id = ?
        ''', (final_score, session_id))
        conn.commit()
        conn.close()

    def record_ai_feedback(self, session_id: int, game_type: str,
                          player_action: str, ai_response: str,
                          outcome: str, difficulty_level: float,
                          learning_data: Dict = None):
        self.init_database()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        learning_json = json.dumps(learning_data) if learning_data else None
        cursor.execute('''
            INSERT INTO ai_feedback 
            (session_id, game_type, player_action, ai_response, outcome,
             difficulty_level, learning_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (session_id, game_type, player_action, ai_response,
              outcome, difficulty_level, learning_json))
        conn.commit()
        conn.close()

    def update_leaderboard(self, player_id: int, game_type: str,
                          score: int, difficulty: float, session_id: int):
        self.init_database()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO leaderboard 
            (player_id, game_type, score, difficulty, session_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (player_id, game_type, score, difficulty, session_id))
        conn.commit()
        conn.close()

    def get_leaderboard(self, game_type: str, limit: int = 10) -> List[Dict]:
        self.init_database()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.session_id, l.score, l.difficulty, l.achieved_at
            FROM leaderboard l
            JOIN players p ON l.player_id = p.id
            WHERE l.game_type = ?
            ORDER BY l.score DESC, l.achieved_at DESC
            LIMIT ?
        ''', (game_type, limit))
        results = []
        for row in cursor.fetchall():
            results.append({
                'session_id': row[0],
                'score': row[1],
                'difficulty': row[2],
                'achieved_at': row[3]
            })
        conn.close()
        return results

    def get_player_stats(self, session_id: str) -> Dict:
        self.init_database()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT total_games, total_score, created_at, last_played
            FROM players WHERE session_id = ?
        ''', (session_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return {
            'total_games': row[0],
            'total_score': row[1],
            'created_at': row[2],
            'last_played': row[3]
        }

    def get_ai_metrics(self, game_type: str) -> Dict:
        self.init_database()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT difficulty_level, win_rate, avg_game_duration, total_games
            FROM ai_metrics WHERE game_type = ?
            ORDER BY difficulty_level
        ''', (game_type,))
        metrics = {}
        for row in cursor.fetchall():
            metrics[row[0]] = {
                'win_rate': row[1],
                'avg_game_duration': row[2],
                'total_games': row[3]
            }
        conn.close()
        return metrics

# Global instance; init_database() is called at startup, not at import
db = ArcadeDatabase()
