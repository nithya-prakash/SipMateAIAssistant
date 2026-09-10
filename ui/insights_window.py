from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ai.insights_engine import InsightsEngine
from tracker.hydration_tracker import HydrationTracker

class InsightsWindow(QWidget):
    def __init__(self, tracker: HydrationTracker, adaptive_scheduler=None):
        super().__init__()
        self.tracker = tracker
        self.adaptive_scheduler = adaptive_scheduler
        self.engine = InsightsEngine(self.tracker)

        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle("SipMate AI Insights")
        self.resize(350, 480)  # taller than the original 400 to fit the new Model section
        self.setStyleSheet("background-color: #1E1E1E; color: white;")

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        title = QLabel("🤖 SipMate learned your habits:")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #333;")
        layout.addWidget(line)
        
        self.lbl_best = QLabel("💧 Best hydration time:\n--")
        self.lbl_best.setFont(QFont("Arial", 14))
        
        self.lbl_worst = QLabel("⚠ You usually forget around:\n--")
        self.lbl_worst.setFont(QFont("Arial", 14))
        
        self.lbl_cons = QLabel("📊 Hydration consistency:\n--")
        self.lbl_cons.setFont(QFont("Arial", 14))
        
        layout.addWidget(self.lbl_best)
        layout.addWidget(self.lbl_worst)
        layout.addWidget(self.lbl_cons)

        # Model section — which algorithm is actually driving predictions,
        # and how well it's cross-validated, not just "AI is on".
        model_line = QFrame()
        model_line.setFrameShape(QFrame.Shape.HLine)
        model_line.setStyleSheet("background-color: #333;")
        layout.addWidget(model_line)

        model_title = QLabel("🧠 Model")
        model_title.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        layout.addWidget(model_title)

        self.lbl_model = QLabel("Collecting data…")
        self.lbl_model.setFont(QFont("Arial", 12))
        self.lbl_model.setWordWrap(True)
        layout.addWidget(self.lbl_model)

        self.setLayout(layout)

    def refresh_data(self):
        insights = self.engine.generate_insights()
        self.lbl_best.setText(f"💧 Best hydration time:\n{insights['best_time']}")
        self.lbl_worst.setText(f"⚠ You usually forget around:\n{insights['worst_time']}")
        self.lbl_cons.setText(f"📊 Hydration consistency:\n{insights['consistency']}")
        self.lbl_model.setText(self._model_summary())

    def _model_summary(self) -> str:
        if self.adaptive_scheduler is None:
            return "Adaptive scheduling not available."
        report = self.adaptive_scheduler.last_evaluation
        if not self.adaptive_scheduler.is_trained or report is None:
            return "Not enough data yet to train and evaluate a model — using your fixed reminder interval in the meantime."
        chosen = report.chosen
        other = next((c for c in report.candidates if c is not chosen), None)
        lines = [
            f"Active model: {chosen.name} (chosen over {other.name} on cross-validated ROC-AUC)" if other else f"Active model: {chosen.name}",
            f"Accuracy: {chosen.accuracy:.0%}  •  ROC-AUC: {chosen.roc_auc:.2f}",
            f"Signal: {chosen.top_signal}",
            f"Trained on {report.sample_count} reminders, {report.folds_used}-fold cross-validated.",
        ]
        return "\n".join(lines)

    def showEvent(self, event):
        self.refresh_data()
        super().showEvent(event)
