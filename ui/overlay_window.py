from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QApplication
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QRect
from PySide6.QtGui import QRegion, QScreen
from renderers.factory import RendererFactory
from ui.speech_bubble import SpeechBubble
from characters.registry import CharacterRegistry
from characters.selector import CharacterSelector
from animations.behaviors import AnimationBehaviors
from sounds.audio_player import AudioPlayer
import random

from core.mac_overlay import enforce_mac_overlay, debug_mac_overlay

class OverlayWindow(QWidget):
    def __init__(self, tracker, settings_manager=None):
        super().__init__()
        self.tracker = tracker
        self.settings_manager = settings_manager
        self.registry = CharacterRegistry()
        self.selector = CharacterSelector(self.registry, settings_manager) if settings_manager else None
        self.audio_player = AudioPlayer()
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.WindowDoesNotAcceptFocus
        )
        
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        self.setLayout(self.layout)
        
        self.mac_timer = QTimer(self)
        self.mac_timer.timeout.connect(self.enforce_overlay)
        
        self.character_widget = None
        self.speech_bubble = None
        
        self.resize(720, 340)

    def trigger_reminder(self, character_id=None):
        import time
        self.trigger_time = time.time()
        
        if character_id:
            character = self.registry.get_character(character_id)
        elif self.selector:
            character = self.selector.select()
        else:
            character = self.registry.get_random_character()
        
        if self.character_widget:
            self.character_widget.deleteLater()
        if self.speech_bubble:
            self.speech_bubble.deleteLater()

        if not self.settings_manager or self.settings_manager.settings.sound_enabled:
            self.audio_player.play_for_character(character.id)

        self.character_widget = RendererFactory.create_renderer(character)
        self.speech_bubble = SpeechBubble("")
        
        # Connect buttons
        self.speech_bubble.btn_drink.clicked.connect(self.on_drank)
        self.speech_bubble.btn_skip.clicked.connect(self.on_skip)
        
        self.layout.addWidget(self.character_widget)
        self.layout.addWidget(self.speech_bubble)
        self.speech_bubble.hide()
        
        # Make sure layout calculations are processed before creating mask
        QApplication.processEvents()
        self.update_click_mask()
        
        # Available desktop geometry
        screen = QApplication.primaryScreen()
        geom = screen.availableGeometry()
        
        # Use behavior
        self.anim_in = AnimationBehaviors.setup_entrance(self, character, geom)
        self.current_character = character
        
        self.anim_in.finished.connect(self.on_entrance_finished)
        
        self.show()
        self.enforce_overlay()
        self.mac_timer.start(500)
        self.anim_in.start()

    def enforce_overlay(self):
        if self.isVisible():
            enforce_mac_overlay(int(self.winId()))

    def update_click_mask(self):
        region = QRegion()
        if self.character_widget and self.character_widget.isVisible():
            region = region.united(QRegion(self.character_widget.geometry()))
        if self.speech_bubble and self.speech_bubble.isVisible():
            region = region.united(QRegion(self.speech_bubble.geometry()))
        self.setMask(region)

    def on_entrance_finished(self):
        if hasattr(self.character_widget, "play_landing_bounce"):
            self.character_widget.play_landing_bounce()

        from ai.message_generator import MessageGenerator
        message = MessageGenerator.generate_message(self.current_character, self.tracker)
        self.speech_bubble.set_text(message)
        self.speech_bubble.show()
        
        # Wait a tiny bit and update mask
        QTimer.singleShot(100, self.update_click_mask)

    def on_drank(self):
        import time
        delay_sec = int(time.time() - getattr(self, 'trigger_time', time.time()))
        self.tracker.log_hydration(250)
        self.tracker.log_reminder(self.current_character.id, True, delay_sec)

        if hasattr(self.character_widget, "play_celebration"):
            self.character_widget.play_celebration()

        # Replace text with toast
        self.speech_bubble.set_text("+1 hydration 💧\nGreat job!")
        self.speech_bubble.btn_drink.hide()
        self.speech_bubble.btn_skip.hide()
        QTimer.singleShot(50, self.update_click_mask)
        
        QTimer.singleShot(1500, self.exit_animation)

    def on_skip(self):
        import time
        delay_sec = int(time.time() - getattr(self, 'trigger_time', time.time()))
        self.tracker.log_reminder(self.current_character.id, False, delay_sec)
        self.exit_animation()

    def exit_animation(self):
        self.speech_bubble.hide()
        self.update_click_mask()
        self.mac_timer.stop()
        
        screen = QApplication.primaryScreen()
        geom = screen.availableGeometry()
        
        self.anim_out = AnimationBehaviors.setup_exit(self, self.current_character, geom)
        self.anim_out.finished.connect(self.hide)
        self.anim_out.start()

    def show_safe_overlay(self):
        self.trigger_reminder()
        debug_mac_overlay(int(self.winId()))
