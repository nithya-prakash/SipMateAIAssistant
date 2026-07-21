import sqlite3
import os
from datetime import datetime
from core.paths import DATA_DIR

class HydrationTracker:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.db_path = os.path.join(DATA_DIR, "hydra.db")
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    hour_of_day INTEGER,
                    day_of_week INTEGER,
                    character_id TEXT,
                    accepted BOOLEAN,
                    response_delay_seconds INTEGER
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS hydration_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    amount_ml INTEGER,
                    source TEXT
                )
            ''')
            conn.commit()

    def log_reminder(self, character_id: str, accepted: bool, delay_sec: int):
        now = datetime.now()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO reminders (timestamp, hour_of_day, day_of_week, character_id, accepted, response_delay_seconds) VALUES (?, ?, ?, ?, ?, ?)",
                (now.isoformat(), now.hour, now.weekday(), character_id, accepted, delay_sec)
            )
            conn.commit()

    def log_hydration(self, amount_ml: int = 250):
        now = datetime.now()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO hydration_logs (timestamp, amount_ml, source) VALUES (?, ?, ?)",
                (now.isoformat(), amount_ml, "overlay")
            )
            conn.commit()
            
    def log_skipped(self):
        # Convenience method to log a skipped reminder
        pass # The reminder was already tracked when triggered, or we can track it here.
            
    def get_reminder_history(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT hour_of_day, day_of_week, accepted FROM reminders")
            return cursor.fetchall()
