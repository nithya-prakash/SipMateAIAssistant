import math
import os
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QPixmap, QFont, QRadialGradient, QBrush
from PySide6.QtCore import Qt, QTimer, QPointF, QRectF, QPropertyAnimation, QEasingCurve, Property

# Characters that already have hand-drawn procedural art in AnimatedVectorWidget.
# We reuse that art as the "graceful placeholder" for these ids instead of a
# generic badge, since it's a strictly nicer fallback when no real asset exists.
_VECTOR_FALLBACK_IDS = {"dog", "cat", "ghost", "airplane", "rocket", "penguin"}

# Data-driven idle-motion parameters per animation_type. Every character gets one
# of these instead of bespoke hand-authored motion, per the "reusable procedural
# animations" requirement. `rectified=True` gives a bouncy hop cadence (abs(sin))
# instead of a smooth bob.
ANIMATION_PROFILES = {
    "bounce":       dict(bob=8,  bob_speed=0.18, scale=0.05,  scale_speed=0.18, rot=0,   rot_speed=0.0,  opacity=0.0),
    "bounce_soft":  dict(bob=5,  bob_speed=0.15, scale=0.03,  scale_speed=0.15, rot=0,   rot_speed=0.0,  opacity=0.0),
    "float":        dict(bob=10, bob_speed=0.06, scale=0.015, scale_speed=0.07, rot=2.0, rot_speed=0.05, opacity=0.08),
    "slow_float":   dict(bob=6,  bob_speed=0.03, scale=0.01,  scale_speed=0.035, rot=1.5, rot_speed=0.025, opacity=0.05),
    "pulse":        dict(bob=2,  bob_speed=0.10, scale=0.07,  scale_speed=0.12, rot=0,   rot_speed=0.0,  opacity=0.0),
    "hop":          dict(bob=14, bob_speed=0.22, scale=0.04,  scale_speed=0.22, rot=0,   rot_speed=0.0,  opacity=0.0, rectified=True),
    "tilt":         dict(bob=3,  bob_speed=0.08, scale=0.0,   scale_speed=0.0,  rot=8.0, rot_speed=0.09, opacity=0.0),
    "sway":         dict(bob=4,  bob_speed=0.10, scale=0.0,   scale_speed=0.0,  rot=6.0, rot_speed=0.10, opacity=0.0),
    "slide_fade":   dict(bob=3,  bob_speed=0.07, scale=0.02,  scale_speed=0.08, rot=0,   rot_speed=0.0,  opacity=0.06),
    "rotate_small": dict(bob=3,  bob_speed=0.09, scale=0.02,  scale_speed=0.09, rot=5.0, rot_speed=0.07, opacity=0.0),
    "launch":       dict(bob=2,  bob_speed=0.30, scale=0.02,  scale_speed=0.30, rot=0,   rot_speed=0.0,  opacity=0.0),
}
_DEFAULT_PROFILE = ANIMATION_PROFILES["bounce_soft"]

_ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "characters")

_CATEGORY_COLORS = {
    "sipmate_original": QColor(90, 170, 250),
    "disney_princess": QColor(220, 130, 200),
    "disney_favorite": QColor(140, 200, 230),
}


def resolve_asset_path(asset_filename: str) -> str:
    if not asset_filename:
        return ""
    path = os.path.join(_ASSETS_DIR, asset_filename)
    return path if os.path.exists(path) else ""


class StaticCharacterWidget(QWidget):
    """Renders a character from a real image asset when one exists, and falls
    back gracefully otherwise - to existing hand-drawn vector art if this id has
    any, or to a generated emoji badge if not. Either way the character gets the
    same procedural life: idle motion (from animation_type), a landing bounce,
    and a celebration animation for "I Drank"."""

    def __init__(self, character, parent=None, autoplay=True):
        super().__init__(parent)
        self.character = character
        self.setFixedSize(140, 140)

        self.tick = 0
        self._squash = 1.0
        self._landing_anim = None
        self._celebrate_ticks_left = 0
        self._outline = QPen(QColor(45, 35, 35, 190), 1.3)

        self._pixmap = self._load_pixmap()
        self._use_vector_fallback = self._pixmap is None and character.id in _VECTOR_FALLBACK_IDS
        self.profile = ANIMATION_PROFILES.get(character.animation_type, _DEFAULT_PROFILE)

        self._last_win_pos = None
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.lag_angle = 0.0
        self._lag_vel = 0.0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)
        if autoplay:
            self.timer.start(33)

    def start_preview(self, duration_ms=2500):
        """Run the idle animation for a little while, then settle back to a static
        pose - used by the Character Collection grid, where every card animating
        nonstop at once would be wasteful and distracting."""
        if not self.timer.isActive():
            self.timer.start(33)
        QTimer.singleShot(duration_ms, self.timer.stop)

    def _load_pixmap(self):
        path = resolve_asset_path(self.character.asset_path)
        if not path:
            return None
        pm = QPixmap(path)
        return pm if not pm.isNull() else None

    # -- public API used by OverlayWindow -----------------------------------

    def play_landing_bounce(self):
        anim = QPropertyAnimation(self, b"squash", self)
        anim.setDuration(550)
        anim.setStartValue(0.62)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutElastic)
        anim.start()
        self._landing_anim = anim

    def play_celebration(self):
        """A bigger, happier beat for a successful "I Drank" - an extra-springy
        bounce plus a brief joyful wobble, layered on top of whatever idle
        animation the character already has."""
        anim = QPropertyAnimation(self, b"squash", self)
        anim.setDuration(700)
        anim.setStartValue(1.35)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutElastic)
        anim.start()
        self._landing_anim = anim
        self._celebrate_ticks_left = 40  # ~1.3s of extra wobble in paintEvent

    # -- Qt property for the landing/celebration bounce ----------------------

    def get_squash(self):
        return self._squash

    def set_squash(self, value):
        self._squash = value
        self.update()

    squash = Property(float, get_squash, set_squash)

    # -- physics / painting ---------------------------------------------------

    def _on_tick(self):
        self.tick += 1
        if self._celebrate_ticks_left > 0:
            self._celebrate_ticks_left -= 1
        self._update_motion_physics()
        self.update()

    def _update_motion_physics(self):
        win = self.window()
        cur = win.pos()
        if self._last_win_pos is not None:
            dx = cur.x() - self._last_win_pos.x()
            dy = cur.y() - self._last_win_pos.y()
        else:
            dx = dy = 0
        self._last_win_pos = cur

        self.vel_x = self.vel_x * 0.65 + dx * 0.35
        self.vel_y = self.vel_y * 0.65 + dy * 0.35

        target = max(-24.0, min(24.0, -self.vel_x * 2.4))
        accel = (target - self.lag_angle) * 0.16
        self._lag_vel = self._lag_vel * 0.72 + accel
        self.lag_angle += self._lag_vel

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        prof = self.profile
        wob = 1.6 if self._celebrate_ticks_left > 0 else 1.0  # extra life while celebrating

        bob_phase = self.tick * prof["bob_speed"]
        bob = abs(math.sin(bob_phase)) if prof.get("rectified") else math.sin(bob_phase)
        bob_y = -bob * prof["bob"] * wob

        scale_pulse = 1.0 + math.sin(self.tick * prof["scale_speed"]) * prof["scale"] * wob
        rot = math.sin(self.tick * prof["rot_speed"]) * prof["rot"] * wob if prof["rot_speed"] else 0.0
        opacity = 1.0 - abs(math.sin(self.tick * 0.05)) * prof["opacity"]

        breathe = 1.0 + math.sin(self.tick * 0.07) * 0.02
        sy = breathe * self._squash * scale_pulse
        sx = breathe * (2.0 - self._squash) * scale_pulse

        self._draw_shadow(p, sy)

        p.save()
        p.setOpacity(max(0.55, opacity))
        p.setPen(self._outline)
        p.translate(70, 70 + bob_y)
        p.rotate(self.lag_angle * 0.25 + rot)
        p.scale(sx, sy)

        if self._pixmap is not None:
            self._draw_pixmap(p)
        elif self._use_vector_fallback:
            self._draw_vector_fallback(p)
        else:
            self._draw_placeholder(p)

        p.restore()
        p.end()

    def _draw_pixmap(self, p):
        target = QRectF(-60, -60, 120, 120)
        p.drawPixmap(target, self._pixmap, QRectF(self._pixmap.rect()))

    def _draw_vector_fallback(self, p):
        # Reuse the existing hand-drawn art directly: these draw_<id> methods only
        # touch self.tick / self.lag_angle / self._outline / self._glossy(), which
        # this widget also provides, so they run unmodified against self here.
        from renderers.vector_assets import AnimatedVectorWidget
        draw_fn = getattr(AnimatedVectorWidget, f"draw_{self.character.id}", None)
        if draw_fn:
            draw_fn(self, p)
        else:
            self._draw_placeholder(p)

    def _glossy(self, color: QColor, w: float, h: float, cx: float = 0.0, cy: float = 0.0) -> QBrush:
        r = max(w, h) * 0.75
        grad = QRadialGradient(cx - w * 0.18, cy - h * 0.28, r)
        grad.setColorAt(0.0, color.lighter(155))
        grad.setColorAt(0.6, color)
        grad.setColorAt(1.0, color.darker(112))
        return QBrush(grad)

    def _draw_placeholder(self, p):
        base = _CATEGORY_COLORS.get(self.character.category, QColor(150, 150, 160))
        p.setBrush(self._glossy(base, 100, 100))
        p.drawEllipse(QPointF(0, 0), 50, 50)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(255, 255, 255, 60))
        p.drawEllipse(QPointF(-15, -18), 22, 14)

        emoji = self.character.emoji or "?"
        p.setPen(QColor(30, 20, 20, 220))
        font = QFont("Apple Color Emoji", 34)
        p.setFont(font)
        p.drawText(QRectF(-50, -50, 100, 100), Qt.AlignmentFlag.AlignCenter, emoji)

    def _draw_shadow(self, p, sy):
        p.save()
        p.setPen(Qt.PenStyle.NoPen)
        width = 60 * (2.0 - sy)
        alpha = max(25, int(70 * sy))
        p.setBrush(QColor(20, 20, 30, alpha))
        p.drawEllipse(QPointF(70, 128), width / 2, 7 * sy)
        p.restore()
