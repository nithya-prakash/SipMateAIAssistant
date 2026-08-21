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
        
        # Load lottie file. Prefer the manifest's own asset filename under
        # assets/characters/ (the same convention StaticCharacterWidget uses);
        # fall back to the older assets/<id>.json / manifests/<id>.json layout.
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        candidates = []
        if getattr(self.character, "asset_path", ""):
            candidates.append(os.path.join(base_dir, "assets", "characters", self.character.asset_path))
        candidates.append(os.path.join(base_dir, "assets", f"{self.character.id}.json"))
        candidates.append(os.path.join(base_dir, "characters", "manifests", f"{self.character.id}.json"))

        filepath = next((p for p in candidates if os.path.exists(p)), candidates[-1])

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

        try:
            # rlottie_python's signature is (frame_num, buffer_size, width, height,
            # bytes_per_line) - all keyword-safe. It returns raw ARGB32-premultiplied
            # bytes, not a numpy array or PIL image.
            buf = self.anim.lottie_animation_render(
                frame_num=self.current_frame,
                width=width,
                height=height,
                bytes_per_line=width * 4,
            )
            img = QImage(buf, width, height, width * 4, QImage.Format.Format_ARGB32_Premultiplied)
            # QImage doesn't copy the buffer by default - keep a reference alive so it
            # isn't garbage-collected out from under the pixmap.
            self._last_buf = buf
            self.label.setPixmap(QPixmap.fromImage(img))
        except Exception as e:
            import logging
            logging.error(f"Lottie render error: {e}")
            self.timer.stop()
            
        self.current_frame = (self.current_frame + 1) % self.total_frames
