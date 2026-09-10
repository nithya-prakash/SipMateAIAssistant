import logging
from datetime import datetime
from typing import Optional

import numpy as np

from ai.model_evaluator import MODEL_BUILDERS, EvaluationReport, evaluate_and_select
from tracker.hydration_tracker import HydrationTracker

logger = logging.getLogger(__name__)


class AdaptiveScheduler:
    def __init__(self, tracker: HydrationTracker):
        self.tracker = tracker
        self.model = None
        self.is_trained = False
        # Last cross-validated evaluation (accuracy/AUC per candidate model,
        # which one was picked, top signal) — surfaced in the AI Insights window.
        self.last_evaluation: Optional[EvaluationReport] = None

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

            report = evaluate_and_select(X, y)
            if report is None:
                # Not enough data to cross-validate meaningfully yet, even
                # though the sample gate above passed — stay untrained rather
                # than ship a model nobody's checked the accuracy of.
                self.is_trained = False
                self.last_evaluation = None
                return

            self.last_evaluation = report
            # Fit the winning algorithm on the full dataset for production use —
            # cross-validation above already told us how well it generalizes.
            self.model = MODEL_BUILDERS[report.chosen.name]().fit(X, y)
            self.is_trained = True
            logger.info(
                "AdaptiveScheduler: trained %s (accuracy=%.2f, AUC=%.2f, %s) on %d samples",
                report.chosen.name, report.chosen.accuracy, report.chosen.roc_auc,
                report.chosen.top_signal, report.sample_count,
            )
        except Exception as e:
            logging.error(f"ML training failed: {e}")
            self.is_trained = False

    def get_probability(self, hour: int, weekday: int) -> float:
        try:
            if not self.is_trained or self.model is None:
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
