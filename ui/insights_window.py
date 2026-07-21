from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ai.insights_engine import InsightsEngine
from tracker.hydration_tracker import HydrationTracker

class InsightsWindow(QWidget):
    def __init__(self, tracker: HydrationTracker):
        super().__init__()
        self.tracker = tracker
        self.engine = InsightsEngine(self.tracker)
        
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle("Hydra AI Insights")
        self.resize(350, 400)
        self.setStyleSheet("background-color: #1E1E1E; color: white;")
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        title = QLabel("🤖 Hydra learned your habits:")
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
        
        self.setLayout(layout)

    def refresh_data(self):
        insights = self.engine.generate_insights()
        self.lbl_best.setText(f"💧 Best hydration time:\n{insights['best_time']}")
        self.lbl_worst.setText(f"⚠ You usually forget around:\n{insights['worst_time']}")
        self.lbl_cons.setText(f"📊 Hydration consistency:\n{insights['consistency']}")
        
    def showEvent(self, event):
        self.refresh_data()
        super().showEvent(event)
