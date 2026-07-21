from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QCursor

class SpeechBubble(QWidget):
    accepted = Signal()
    skipped = Signal()

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Container to hold everything with a white background
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 245);
                border-radius: 12px;
            }
        """)
        
        layout = QVBoxLayout(container)
        
        self.label = QLabel(text)
        self.label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.label.setStyleSheet("color: #333; background: transparent;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        
        # Action Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_drink = QPushButton("💧 I Drank")
        self.btn_drink.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_drink.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #005bb5; }
        """)
        self.btn_drink.clicked.connect(self.accepted.emit)
        
        self.btn_skip = QPushButton("Skip")
        self.btn_skip.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_skip.setStyleSheet("""
            QPushButton {
                background-color: #E5E5EA;
                color: #333;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
            }
            QPushButton:hover { background-color: #D1D1D6; }
        """)
        self.btn_skip.clicked.connect(self.skipped.emit)
        
        btn_layout.addWidget(self.btn_drink)
        btn_layout.addWidget(self.btn_skip)
        layout.addLayout(btn_layout)
        
        main_layout.addWidget(container)
        self.setLayout(main_layout)
        
        self.hide()
        
    def set_text(self, text: str):
        self.label.setText(text)
        self.adjustSize()
