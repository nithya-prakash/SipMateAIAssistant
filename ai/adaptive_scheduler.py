import numpy as np
from sklearn.linear_model import LogisticRegression
from tracker.hydration_tracker import HydrationTracker
from datetime import datetime

class AdaptiveScheduler:
    def __init__(self, tracker: HydrationTracker):
        self.tracker = tracker
        self.model = LogisticRegression()
        self.is_trained = False
        
    def _encode_features(self, hour: int, weekday: int) -> list:
        return [
            np.sin(2 * np.pi * hour / 24.0),
            np.cos(2 * np.pi * hour / 24.0),
            np.sin(2 * np.pi * weekday / 7.0),
            np.cos(2 * np.pi * weekday / 7.0)
        ]

    def train_model(self):
        try:
            history = self.tracker.get_reminder_history()
            
            # Need minimum data to train (min 20 samples)
            if len(history) < 20:
                self.is_trained = False
                return
                
            X = np.array([self._encode_features(row[0], row[1]) for row in history])
            y = np.array([1 if row[2] else 0 for row in history])
            
            # Ensure we have both accepted and rejected classes, with at least 3 samples each
            if len(set(y)) < 2 or sum(y) < 3 or (len(y) - sum(y)) < 3:
                self.is_trained = False
                return
                
            self.model.fit(X, y)
            self.is_trained = True
        except Exception as e:
            import logging
            logging.error(f"ML training failed: {e}")
            self.is_trained = False

    def get_probability(self, hour: int, weekday: int) -> float:
        try:
            if not self.is_trained:
                return 0.5
                
            X_pred = np.array([self._encode_features(hour, weekday)])
            return self.model.predict_proba(X_pred)[0][1]
        except Exception:
            return 0.5

    def get_next_optimal_reminder_minutes(self) -> int:
        """
        Determines optimal interval. Fallback to 60 mins if untrained.
        """
        if not self.is_trained:
            return 60
            
        now = datetime.now()
        current_hour = now.hour
        weekday = now.weekday()
        
        best_prob = 0
        best_hour_offset = 1
        
        for offset in range(1, 4):
            hour_to_check = (current_hour + offset) % 24
            prob = self.get_probability(hour_to_check, weekday)
            if prob > best_prob:
                best_prob = prob
                best_hour_offset = offset
                
        if best_prob > 0.6:
            return best_hour_offset * 60
        else:
            return 60
