"""Trains and evaluates candidate reminder-response models, honestly.

`AdaptiveScheduler` used to just call `LogisticRegression().fit(X, y)` on
100% of the data with no held-out check and no comparison against any
alternative — there was no way to know whether the model was actually any
good. This module fixes that: it fits two different algorithms, scores each
on unseen data, and reports back which one actually generalizes better, plus
which features it's leaning on.

The dataset here is inherently small (a few dozen to a few hundred reminder
events for one person), so this deliberately doesn't pretend to be a
large-scale ML evaluation — it uses stratified k-fold cross-validation
(falling back gracefully when there isn't enough data per class for even
that) rather than a single train/test split, since a single small hold-out
set would be noisy enough to be misleading.
"""
from __future__ import annotations

import logging
import warnings
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from sklearn.exceptions import UndefinedMetricWarning
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict, cross_val_score

logger = logging.getLogger(__name__)

# Collapses the 4 cyclical (sin/cos) columns back to 2 human-readable factors.
FEATURE_COLUMN_GROUPS = {
    "time of day": (0, 1),
    "day of week": (2, 3),
}

MIN_FOLDS = 3
# StratifiedKFold only requires n_splits <= the smallest class count; 1 keeps
# this aligned with AdaptiveScheduler's existing "at least 3 of each class"
# gate (3 // 1 = 3 folds) rather than silently demanding more data than that
# gate promises.
MIN_SAMPLES_PER_FOLD_CLASS = 1

# Shared with AdaptiveScheduler so the model it fits on 100% of the data for
# production use has the exact hyperparameters that were actually evaluated.
MODEL_BUILDERS = {
    "Logistic Regression": lambda: LogisticRegression(max_iter=500),
    "Random Forest": lambda: RandomForestClassifier(n_estimators=100, max_depth=4, random_state=0),
}


@dataclass
class ModelResult:
    name: str
    accuracy: float
    precision: float
    recall: float
    roc_auc: float
    top_signal: str


@dataclass
class EvaluationReport:
    chosen: ModelResult
    candidates: list[ModelResult] = field(default_factory=list)
    sample_count: int = 0
    folds_used: int = 0


def _n_folds(y: np.ndarray) -> int:
    """The largest k<=5 for which every class still has >=MIN_SAMPLES_PER_FOLD_CLASS per fold."""
    counts = np.bincount(y.astype(int))
    smallest_class = counts[counts > 0].min()
    max_folds = smallest_class // MIN_SAMPLES_PER_FOLD_CLASS
    return int(max(0, min(5, max_folds)))


def _describe_top_signal(model, X: np.ndarray, y: np.ndarray) -> str:
    """Permutation importance, collapsed to 'time of day' vs 'day of week' —
    reported as a rough signal, not a precise statistical claim."""
    try:
        result = permutation_importance(model, X, y, n_repeats=10, random_state=0, scoring="roc_auc")
        grouped = {
            label: float(result.importances_mean[list(cols)].sum())
            for label, cols in FEATURE_COLUMN_GROUPS.items()
        }
        best = max(grouped, key=grouped.get)
        if grouped[best] <= 0:
            return "no single factor clearly dominates yet"
        return f"{best} matters most"
    except Exception:
        logger.exception("model_evaluator: permutation importance failed")
        return "unavailable"


def _evaluate_one(name: str, build_model, X: np.ndarray, y: np.ndarray, folds: int) -> ModelResult:
    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=0)
    # On small folds a candidate can end up predicting no positives at all —
    # precision/recall are genuinely undefined there (reported as 0, not an
    # error), so this is an expected edge case to silence, not a real warning.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UndefinedMetricWarning)
        accuracy = float(np.mean(cross_val_score(build_model(), X, y, cv=cv, scoring="accuracy")))
        precision = float(np.mean(cross_val_score(build_model(), X, y, cv=cv, scoring="precision", error_score=0)))
        recall = float(np.mean(cross_val_score(build_model(), X, y, cv=cv, scoring="recall", error_score=0)))
        probabilities = cross_val_predict(build_model(), X, y, cv=cv, method="predict_proba")[:, 1]

    roc_auc = float(roc_auc_score(y, probabilities))

    fitted = build_model().fit(X, y)
    top_signal = _describe_top_signal(fitted, X, y)

    return ModelResult(name=name, accuracy=accuracy, precision=precision, recall=recall,
                        roc_auc=roc_auc, top_signal=top_signal)


def evaluate_and_select(X: np.ndarray, y: np.ndarray) -> Optional[EvaluationReport]:
    """Fits + cross-validates LogisticRegression and RandomForest, returns
    whichever scores higher on ROC-AUC. Returns None (never raises) if there
    isn't enough data to evaluate meaningfully."""
    folds = _n_folds(y)
    if folds < MIN_FOLDS:
        logger.info("model_evaluator: only %d viable folds (<%d) — skipping evaluation", folds, MIN_FOLDS)
        return None

    try:
        candidates = [
            _evaluate_one(name, builder, X, y, folds)
            for name, builder in MODEL_BUILDERS.items()
        ]
    except Exception:
        logger.exception("model_evaluator: evaluation failed")
        return None

    chosen = max(candidates, key=lambda r: r.roc_auc)
    logger.info(
        "model_evaluator: selected %s (AUC=%.2f) over %s (AUC=%.2f) on %d samples, %d folds",
        chosen.name, chosen.roc_auc,
        next(c for c in candidates if c is not chosen).name,
        next(c for c in candidates if c is not chosen).roc_auc,
        len(y), folds,
    )
    return EvaluationReport(chosen=chosen, candidates=candidates, sample_count=len(y), folds_used=folds)
