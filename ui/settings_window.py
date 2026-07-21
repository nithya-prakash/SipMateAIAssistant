from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class SettingsWindow(QWidget):
    def __init__(self, settings_manager):
        super().__init__()
        
        self.settings_manager = settings_manager
        
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle("SipMate Settings")
        self.resize(300, 300)
        self.setStyleSheet("background-color: #f5f5f7; color: #1d1d1f;")
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("SipMate Settings")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(title)
        
        self.chk_adaptive = QCheckBox("Enable AI Adaptive Scheduling")
        self.chk_adaptive.setChecked(self.settings_manager.settings.ai_adaptive_scheduling_enabled)
        self.chk_adaptive.toggled.connect(lambda checked: self.settings_manager.update(ai_adaptive_scheduling_enabled=checked))
        layout.addWidget(self.chk_adaptive)
        
        self.chk_dynamic = QCheckBox("Enable Dynamic AI Messages")
        self.chk_dynamic.setChecked(self.settings_manager.settings.ai_dynamic_messages_enabled)
        self.chk_dynamic.toggled.connect(lambda checked: self.settings_manager.update(ai_dynamic_messages_enabled=checked))
        layout.addWidget(self.chk_dynamic)
        
        self.chk_sound = QCheckBox("Play Notification Sound")
        self.chk_sound.setChecked(self.settings_manager.settings.sound_enabled)
        self.chk_sound.toggled.connect(lambda checked: self.settings_manager.update(sound_enabled=checked))
        layout.addWidget(self.chk_sound)
        
        layout.addStretch()
        
        close_btn = QPushButton("Save & Close")
        close_btn.setStyleSheet("background-color: #007AFF; color: white; padding: 10px; border-radius: 5px;")
        close_btn.clicked.connect(self.hide)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
