from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QPushButton, QComboBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

CHARACTER_MODES = [
    ("random", "Random - any of the 8 characters"),
    ("single", "Single Character - whichever you Selected in the Collection"),
    ("daily_rotation", "Daily Rotation - a new character each day"),
    ("favorites", "Favorites - random from your favorited characters"),
]

class SettingsWindow(QWidget):
    def __init__(self, settings_manager):
        super().__init__()
        
        self.settings_manager = settings_manager
        
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle("SipMate Settings")
        self.resize(340, 440)
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

        mode_label = QLabel("Character Mode")
        mode_label.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        layout.addWidget(mode_label)

        self.combo_mode = QComboBox()
        for value, label in CHARACTER_MODES:
            self.combo_mode.addItem(label, userData=value)
        current = self.settings_manager.settings.character_mode
        idx = next((i for i, (v, _) in enumerate(CHARACTER_MODES) if v == current), 0)
        self.combo_mode.setCurrentIndex(idx)
        self.combo_mode.currentIndexChanged.connect(
            lambda i: self.settings_manager.update(character_mode=self.combo_mode.itemData(i))
        )
        layout.addWidget(self.combo_mode)

        layout.addStretch()
        
        close_btn = QPushButton("Save & Close")
        close_btn.setStyleSheet("background-color: #007AFF; color: white; padding: 10px; border-radius: 5px;")
        close_btn.clicked.connect(self.hide)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
