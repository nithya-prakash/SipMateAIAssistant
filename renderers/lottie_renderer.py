from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QTimer, Qt
import os
import rlottie_python as rlottie
from characters.character import Character

class LottieRenderer(QWidget):
    def __init__(self, character: Character):
        super().__init__()
        self.character = character
        self.setFixedSize(150, 150)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.label = QLabel(self)
        self.label.setFixedSize(150, 150)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        
        # Load lottie file
        # Check if file exists, else use fallback
        filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", f"{self.character.id}.json")
        if not os.path.exists(filepath):
            # Fallback path if it's in manifests directly
            filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "characters", "manifests", f"{self.character.id}.json")

        if os.path.exists(filepath):
            self.anim = rlottie.LottieAnimation.from_file(filepath)
            self.total_frames = self.anim.lottie_animation_get_totalframe()
            self.framerate = self.anim.lottie_animation_get_framerate()
        else:
            self.anim = None
            self.total_frames = 1
            self.framerate = 30
            import logging
            logging.warning(f"Lottie file not found for {self.character.id} at {filepath}")
            
        self.current_frame = 0
        self.timer = QTimer(self)
        
        # typically 30 fps is ~33ms
        interval = int(1000 / self.framerate) if self.framerate > 0 else 33
        self.timer.timeout.connect(self._update_frame)
        self.timer.start(interval)
        
        self._update_frame()
        
    def _update_frame(self):
        if not self.anim:
            return
            
        # rlottie-python render_pillow_frame may return a PIL Image or similar, 
        # but the standard raw render is often better. Let's use it if possible.
        # However, rlottie_python doesn't easily expose raw buffer to python. 
        # render_pillow_frame is easiest if Pillow is installed, but we may not have Pillow.
        # lottie_animation_render(frame_num, width, height, bytes_per_line) ?
        
        width = 150
        height = 150
        
        # Using lottie_animation_render
        # It takes (frame_num, width, height) and returns a tuple (buffer, bytes_per_line) or something similar.
        # Let's wrap in try/except to inspect what it returns.
        try:
            buf = self.anim.lottie_animation_render(self.current_frame, width, height)
            # rlottie_python's lottie_animation_render returns a numpy array or bytes?
            # actually rlottie_python usually returns a 3D numpy array (height, width, 4) in BGRA.
            if hasattr(buf, "shape"): # numpy array
                img = QImage(buf.data, width, height, width * 4, QImage.Format.Format_ARGB32_Premultiplied)
                # ARGB32 vs BGRA - might need to swap if colors are weird, but usually QImage handles it
                # rlottie uses BGRA32 natively. QImage.Format_ARGB32_Premultiplied is usually BGRA under the hood in Qt on little endian.
            else:
                img = QImage(buf, width, height, width * 4, QImage.Format.Format_ARGB32_Premultiplied)
                
            self.label.setPixmap(QPixmap.fromImage(img))
        except Exception as e:
            import logging
            logging.error(f"Lottie render error: {e}")
            self.timer.stop()
            
        self.current_frame = (self.current_frame + 1) % self.total_frames
