"""Verifies the strengthened adaptive scheduler: real cross-validated
evaluation, model comparison, and a fallback that never crashes."""
import random

from ai.adaptive_scheduler import AdaptiveScheduler


class FakeTracker:
    def __init__(self, history):
        self.history = history

    def get_reminder_history(self):
        return self.history


# 1. A clear synthetic pattern (10am reliably accepted, 1am reliably ignored) —
#    the model should learn it and evaluation should reflect that.
random.seed(42)
history = []
for _ in range(80):
    hour = random.choice([10] * 5 + [1] * 5)
    weekday = random.randint(0, 6)
    accepted = (hour == 10 and random.random() < 0.85) or (hour == 1 and random.random() < 0.1)
    history.append((hour, weekday, accepted))

scheduler = AdaptiveScheduler(FakeTracker(history))
scheduler.train_model()

assert scheduler.is_trained, "expected model to train on 80 clearly-patterned samples"
assert scheduler.last_evaluation is not None, "expected an evaluation report"
assert len(scheduler.last_evaluation.candidates) == 2, "expected both models to be evaluated"
assert scheduler.last_evaluation.chosen.roc_auc >= 0.5, "chosen model should beat random guessing"

prob_good = scheduler.get_probability(10, 2)
prob_bad = scheduler.get_probability(1, 2)
assert prob_good > prob_bad, f"expected 10am ({prob_good:.2f}) to score higher than 1am ({prob_bad:.2f})"

print(f"Chosen model: {scheduler.last_evaluation.chosen.name}")
print(f"  accuracy={scheduler.last_evaluation.chosen.accuracy:.2f} "
      f"roc_auc={scheduler.last_evaluation.chosen.roc_auc:.2f} "
      f"signal='{scheduler.last_evaluation.chosen.top_signal}'")
print(f"  P(respond | 10am) = {prob_good:.2f}, P(respond | 1am) = {prob_bad:.2f}")
print("Pattern learned correctly.")

# 2. Not enough data yet — should stay untrained, not crash, fall back to 0.5.
scheduler_new = AdaptiveScheduler(FakeTracker([(10, 0, True)] * 5))
scheduler_new.train_model()
assert not scheduler_new.is_trained
assert scheduler_new.get_probability(10, 0) == 0.5
print("New-user fallback verified (untrained -> 0.5, no crash).")

# 3. Malformed data should never propagate an exception.
class BrokenTracker:
    def get_reminder_history(self):
        return [(None, None, True)] * 25 + [(1, 1, False)] * 5


scheduler_broken = AdaptiveScheduler(BrokenTracker())
scheduler_broken.train_model()  # must not raise
assert not scheduler_broken.is_trained
assert scheduler_broken.get_probability(10, 0) == 0.5
print("Malformed-data fallback verified (no crash, stayed untrained).")

print("\nAll adaptive scheduler checks passed.")
