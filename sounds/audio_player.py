from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtCore import QUrl
import subprocess
import os

class AudioPlayer:
    def __init__(self):
        self.effect = QSoundEffect()
        # Use macOS default Glass sound for now
        self.sound_path = "/System/Library/Sounds/Glass.aiff"
        if os.path.exists(self.sound_path):
            self.effect.setSource(QUrl.fromLocalFile(self.sound_path))
            self.effect.setVolume(0.5)
            
    def play_ting(self):
        if self.effect.source().isValid():
            self.effect.play()
        else:
            # Fallback to afplay if QtMultimedia fails to load the sound
            subprocess.Popen(['afplay', self.sound_path])
