from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QPainterPath, QRadialGradient, QBrush
from PySide6.QtCore import Qt, QTimer, QPointF, QPropertyAnimation, QEasingCurve, Property
import math
import random


class AnimatedVectorWidget(QWidget):
    def __init__(self, character_id, parent=None):
        super().__init__(parent)
        self.character_id = character_id
        self.setFixedSize(140, 140)

        self.tick = 0
        self._squash = 1.0
        self._landing_anim = None
        self._outline = QPen(QColor(45, 35, 35, 190), 1.3)

        # Motion-driven secondary animation: track how fast the window itself is moving
        # (it's what the entrance/exit path in behaviors.py actually animates) and turn
        # that into a lean + a damped-spring lag, so ears/tails trail behind the body and
        # gradually catch up instead of wiggling on a fixed idle timer.
        self._last_win_pos = None
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.lag_angle = 0.0
        self._lag_vel = 0.0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(33)  # ~30fps, smoother than a choppy 20fps tick

    def update_animation(self):
        self.tick += 1
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

        # Low-pass filter so single-pixel jitter doesn't read as a twitch
        self.vel_x = self.vel_x * 0.65 + dx * 0.35
        self.vel_y = self.vel_y * 0.65 + dy * 0.35

        # Critically-damped spring chasing a lean target set by horizontal speed.
        # The overshoot-then-settle is what gives ears/tails real follow-through
        # instead of a metronome wiggle.
        target = max(-24.0, min(24.0, -self.vel_x * 2.4))
        accel = (target - self.lag_angle) * 0.16
        self._lag_vel = self._lag_vel * 0.72 + accel
        self.lag_angle += self._lag_vel

    def get_squash(self):
        return self._squash

    def set_squash(self, value):
        self._squash = value
        self.update()

    squash = Property(float, get_squash, set_squash)

    def play_landing_bounce(self):
        """Squash on impact, spring back with a slight overshoot - classic squash & stretch."""
        anim = QPropertyAnimation(self, b"squash", self)
        anim.setDuration(550)
        anim.setStartValue(0.62)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutElastic)
        anim.start()
        self._landing_anim = anim

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        breathe = 1.0 + math.sin(self.tick * 0.07) * 0.02

        # Speed stretch: fast horizontal travel stretches the silhouette along its
        # direction of motion and squeezes it thinner the other way (and vertical
        # speed - rising or falling fast - does the same on that axis). This is on
        # top of the discrete landing-impact squash, so motion feels alive throughout
        # the flight, not just at touchdown.
        speed_stretch_x = max(-0.22, min(0.22, abs(self.vel_x) * 0.02))
        speed_stretch_y = max(-0.22, min(0.22, abs(self.vel_y) * 0.03))

        sy = breathe * self._squash * (1.0 - speed_stretch_x * 0.5 + speed_stretch_y)
        sx = breathe * (2.0 - self._squash) * (1.0 + speed_stretch_x - speed_stretch_y * 0.4)

        self._draw_shadow(painter, sy)

        painter.save()
        painter.setPen(self._outline)
        painter.translate(70, 70)
        painter.rotate(self.lag_angle * 0.25)  # subtle whole-body lean into the motion
        painter.scale(sx, sy)

        func = getattr(self, f"draw_{self.character_id}", self.draw_placeholder)
        func(painter)

        painter.restore()
        painter.end()

    def _draw_shadow(self, p, sy):
        p.save()
        p.setPen(Qt.PenStyle.NoPen)
        width = 60 * (2.0 - sy)
        alpha = max(25, int(70 * sy))
        p.setBrush(QColor(20, 20, 30, alpha))
        p.drawEllipse(QPointF(70, 128), width / 2, 7 * sy)
        p.restore()

    def _glossy(self, color: QColor, w: float, h: float, cx: float = 0.0, cy: float = 0.0) -> QBrush:
        """Soft radial highlight over a base color - rounded cel-shaded look instead of a flat fill."""
        r = max(w, h) * 0.75
        grad = QRadialGradient(cx - w * 0.18, cy - h * 0.28, r)
        grad.setColorAt(0.0, color.lighter(155))
        grad.setColorAt(0.6, color)
        grad.setColorAt(1.0, color.darker(112))
        return QBrush(grad)

    def draw_airplane(self, p):
        p.rotate(15 * math.sin(self.tick * 0.1))

        if self.tick % 4 < 2:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(200, 200, 200, 150))
            p.drawEllipse(-80, 0, 15, 15)
            p.drawEllipse(-100, 5, 10, 10)
            p.setPen(self._outline)

        p.setBrush(self._glossy(QColor(50, 150, 250), 80, 30))
        p.drawRoundedRect(-40, -15, 80, 30, 14, 14)
        p.setBrush(self._glossy(QColor(210, 212, 215), 20, 20))
        p.drawRoundedRect(-10, -35, 20, 20, 6, 6)

        p.rotate(self.tick * 20)
        p.setBrush(QColor(110, 110, 110))
        p.drawEllipse(35, -20, 10, 40)

    def draw_cat(self, p):
        y_offset = math.sin(self.tick * 0.15) * 4
        p.translate(0, y_offset)

        tail_rot = math.sin(self.tick * 0.2) * 20
        p.save()
        p.translate(-30, 0)
        p.rotate(tail_rot)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(255, 150, 50))
        p.drawEllipse(-20, -5, 30, 10)
        p.restore()

        p.setPen(self._outline)
        p.setBrush(self._glossy(QColor(255, 150, 50), 60, 40))
        p.drawEllipse(-30, -20, 60, 40)
        p.drawEllipse(10, -40, 30, 30)

        p.setBrush(self._glossy(QColor(255, 150, 50), 30, 30))
        path = QPainterPath()
        path.moveTo(15, -35)
        path.lineTo(20, -55)
        path.lineTo(30, -35)
        p.drawPath(path)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(0, 0, 0))
        if self.tick % 40 < 3:
            p.drawRoundedRect(20, -30, 5, 2, 1, 1)
            p.drawRoundedRect(30, -30, 5, 2, 1, 1)
        else:
            p.drawEllipse(20, -32, 5, 5)
            p.drawEllipse(30, -32, 5, 5)

    def draw_dog(self, p):
        y_offset = math.sin(self.tick * 0.2) * 6
        p.translate(0, y_offset)

        # Tail: idle wag plus a much bigger, spring-lagged trail that whips
        # opposite the direction of travel and overshoots as it catches up -
        # this is the follow-through, not the wag; the wag is just texture on top.
        tail_rot = math.sin(self.tick * 0.4) * 18 - self.lag_angle * 1.15
        p.save()
        p.translate(-30, 0)
        p.rotate(tail_rot)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(139, 69, 19))
        p.drawEllipse(-20, -5, 30, 15)
        p.restore()

        # Head leads the lean slightly ahead of the body (anticipation) while the
        # torso itself only carries the whole-body lean applied in paintEvent.
        p.save()
        p.rotate(self.lag_angle * -0.12)

        p.setPen(self._outline)
        p.setBrush(self._glossy(QColor(160, 82, 45), 60, 40))
        p.drawEllipse(-30, -20, 60, 40)
        p.drawEllipse(10, -35, 35, 35)

        # Floppy ear: hangs from the head and lags/swings with real weight.
        p.save()
        p.translate(20, -22)
        p.rotate(8 + self.lag_angle * 0.9)
        p.setBrush(QColor(100, 50, 10))
        p.drawEllipse(-5, 0, 10, 25)
        p.restore()

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(Qt.GlobalColor.black)
        p.drawEllipse(35, -25, 5, 5)

        p.setPen(self._outline)
        p.setBrush(QColor(100, 200, 255))
        p.drawRoundedRect(40, -15, 20, 10, 4, 4)
        p.restore()

    def draw_girl(self, p):
        y_offset = math.sin(self.tick * 0.1) * 3
        p.translate(0, y_offset)

        p.setBrush(self._glossy(QColor(150, 100, 200), 30, 50))
        p.drawRoundedRect(-15, -10, 30, 50, 12, 12)

        p.setBrush(self._glossy(QColor(255, 220, 177), 40, 40))
        p.drawEllipse(-20, -50, 40, 40)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(50, 30, 10))
        path = QPainterPath()
        path.addEllipse(-22, -52, 44, 25)
        p.drawPath(path)
        p.setPen(self._outline)

        arm_rot = math.sin(self.tick * 0.2) * 30 if self.tick % 60 < 30 else 0
        p.save()
        p.translate(15, -5)
        p.rotate(arm_rot - 45)
        p.setBrush(QColor(255, 220, 177))
        p.drawEllipse(0, 0, 25, 8)
        p.restore()

        p.setBrush(QColor(100, 200, 255))
        p.drawRoundedRect(-25, -20, 10, 20, 4, 4)

    def draw_rocket(self, p):
        y_shake = math.sin(self.tick * 0.5) * 1.5
        p.translate(0, y_shake)

        # A climbing rocket doesn't fly perfectly straight - it wobbles off-axis
        # and corrects, which reads far more alive than a rigid vertical line.
        p.rotate(self.lag_angle * 0.5 + math.sin(self.tick * 0.13) * 3)

        # Thrust exaggerates with actual climb speed: barely-there on liftoff,
        # a long roaring plume once it's really moving.
        climb_speed = max(0.0, -self.vel_y)
        flame_stretch = 1.0 + min(1.6, climb_speed * 0.18)
        if self.tick % 2 == 0:
            p.save()
            p.scale(1.0, flame_stretch)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(255, 100, 0))
            p.drawEllipse(-15, 30, 30, 40)
            p.setBrush(QColor(255, 200, 0))
            p.drawEllipse(-10, 30, 20, 25)
            p.restore()
            p.setPen(self._outline)

        p.setBrush(self._glossy(QColor(210, 210, 215), 40, 80))
        p.drawEllipse(-20, -40, 40, 80)

        p.setBrush(self._glossy(QColor(100, 200, 255), 20, 20))
        p.drawEllipse(-10, -20, 20, 20)

        p.setBrush(QColor(255, 50, 50))
        path = QPainterPath()
        path.moveTo(-20, 10)
        path.lineTo(-40, 40)
        path.lineTo(-20, 30)
        p.drawPath(path)
        path = QPainterPath()
        path.moveTo(20, 10)
        path.lineTo(40, 40)
        path.lineTo(20, 30)
        p.drawPath(path)

    def draw_robot(self, p):
        if self.tick % 50 == 0:
            p.translate(random.randint(-4, 4), random.randint(-4, 4))

        p.setBrush(self._glossy(QColor(150, 160, 170), 50, 50))
        p.drawRoundedRect(-25, -20, 50, 50, 10, 10)

        p.drawRoundedRect(-30, -70, 60, 50, 12, 12)

        p.drawLine(0, -70, 0, -90)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(255, 0, 0) if self.tick % 10 < 5 else QColor(100, 0, 0))
        p.drawEllipse(-5, -95, 10, 10)
        p.setPen(self._outline)

        p.setBrush(self._glossy(QColor(0, 255, 255), 15, 10))
        p.drawRoundedRect(-20, -55, 15, 10, 3, 3)
        p.drawRoundedRect(5, -55, 15, 10, 3, 3)

    def draw_penguin(self, p):
        rot = math.sin(self.tick * 0.15) * 8
        p.rotate(rot)

        p.setBrush(self._glossy(QColor(30, 30, 35), 50, 80))
        p.drawEllipse(-25, -40, 50, 80)

        p.setBrush(self._glossy(QColor(255, 255, 255), 30, 50))
        p.drawEllipse(-15, -20, 30, 50)

        p.setBrush(QColor(255, 150, 0))
        path = QPainterPath()
        path.moveTo(-5, -30)
        path.lineTo(5, -30)
        path.lineTo(0, -20)
        p.drawPath(path)

    def draw_panda(self, p):
        y_offset = math.sin(self.tick * 0.12) * 3
        p.translate(0, y_offset)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(Qt.GlobalColor.black)
        p.drawEllipse(-35, -45, 20, 20)
        p.drawEllipse(15, -45, 20, 20)
        p.setPen(self._outline)

        p.setBrush(self._glossy(QColor(250, 250, 250), 80, 70))
        p.drawEllipse(-40, -40, 80, 70)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(Qt.GlobalColor.black)
        p.drawEllipse(-25, -20, 20, 25)
        p.drawEllipse(5, -20, 20, 25)

        p.setBrush(Qt.GlobalColor.white)
        p.drawEllipse(-20, -15, 8, 8)
        p.drawEllipse(10, -15, 8, 8)

    def draw_butterfly(self, p):
        y_offset = math.sin(self.tick * 0.1) * 8
        p.translate(0, y_offset)

        wing_scale = math.sin(self.tick * 0.35) * 0.5 + 0.5

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(self._glossy(QColor(255, 100, 200), 30, 40))
        p.drawEllipse(-30 * wing_scale, -20, 30 * wing_scale, 40)
        p.drawEllipse(0, -20, 30 * wing_scale, 40)

        p.setBrush(QColor(50, 50, 50))
        p.drawEllipse(-5, -30, 10, 60)

    def draw_ghost(self, p):
        y_offset = math.sin(self.tick * 0.07) * 12
        p.translate(0, y_offset)

        alpha = int(200 + math.sin(self.tick * 0.04) * 50)
        p.setBrush(QColor(240, 240, 255, alpha))
        p.setPen(Qt.PenStyle.NoPen)

        path = QPainterPath()
        path.moveTo(-30, 40)
        path.lineTo(-30, -20)
        path.arcTo(-30, -50, 60, 60, 180, -180)
        path.lineTo(30, 40)
        for i in range(3):
            path.quadTo(20 - i * 20, 50, 10 - i * 20, 40)

        p.drawPath(path)

        p.setBrush(QColor(0, 0, 0, alpha))
        p.drawEllipse(-15, -20, 10, 15)
        p.drawEllipse(5, -20, 10, 15)
        p.drawEllipse(-5, 0, 10, 10)

    def draw_cow(self, p):
        y_offset = math.sin(self.tick * 0.15) * 3
        p.translate(0, y_offset)

        p.setBrush(self._glossy(QColor(255, 255, 255), 80, 50))
        p.drawRoundedRect(-40, -20, 80, 50, 16, 16)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(Qt.GlobalColor.black)
        p.drawEllipse(-30, -10, 20, 20)
        p.drawEllipse(10, 0, 25, 20)
        p.setPen(self._outline)

        p.setBrush(self._glossy(QColor(255, 255, 255), 30, 30))
        p.drawEllipse(20, -35, 30, 30)

        chew = math.sin(self.tick * 0.3) * 2
        p.setBrush(QColor(255, 180, 180))
        p.drawEllipse(35, -25 + chew, 15, 20)

    def draw_wizard(self, p):
        sway = math.sin(self.tick * 0.1) * 3
        p.rotate(sway * 0.4)

        p.setBrush(self._glossy(QColor(100, 50, 200), 40, 50))
        p.drawRoundedRect(-20, -10, 40, 50, 10, 10)

        path = QPainterPath()
        path.moveTo(-30, -30)
        path.lineTo(30, -30)
        path.lineTo(0, -80)
        p.setBrush(self._glossy(QColor(100, 50, 200), 60, 50))
        p.drawPath(path)

        p.setBrush(self._glossy(QColor(255, 200, 150), 30, 25))
        p.drawEllipse(-15, -30, 30, 25)

        p.setBrush(QColor(220, 220, 220))
        path = QPainterPath()
        path.moveTo(-15, -15)
        path.lineTo(15, -15)
        path.lineTo(0, 10)
        p.drawPath(path)

    def draw_alien(self, p):
        p.translate(0, math.sin(self.tick * 0.08) * 10)

        p.setBrush(self._glossy(QColor(120, 120, 125), 100, 30))
        p.drawEllipse(-50, 10, 100, 30)

        p.setBrush(QColor(150, 255, 255, 150))
        p.drawEllipse(-30, -20, 60, 50)

        p.setBrush(self._glossy(QColor(50, 255, 50), 30, 30))
        p.drawEllipse(-15, -10, 30, 30)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(Qt.GlobalColor.black)
        p.drawEllipse(-10, -5, 8, 12)
        p.drawEllipse(2, -5, 8, 12)

    def draw_dragon(self, p):
        p.translate(0, math.sin(self.tick * 0.15) * 8)

        p.setBrush(self._glossy(QColor(200, 50, 50), 60, 40))
        p.drawEllipse(-30, -20, 60, 40)
        p.drawEllipse(15, -40, 30, 30)

        if self.tick % 10 < 5:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(255, 100, 0))
            path = QPainterPath()
            path.moveTo(40, -30)
            path.lineTo(80, -20)
            path.lineTo(80, -40)
            p.drawPath(path)

    def draw_eiffel_tower(self, p):
        p.setBrush(self._glossy(QColor(150, 150, 160), 60, 40))

        path = QPainterPath()
        path.moveTo(-30, 40)
        path.lineTo(30, 40)
        path.lineTo(15, 0)
        path.lineTo(-15, 0)
        p.drawPath(path)

        path = QPainterPath()
        path.moveTo(-10, 0)
        path.lineTo(10, 0)
        path.lineTo(0, -60)
        p.drawPath(path)

        if self.tick % 8 == 0:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(255, 255, 200))
            px = random.randint(-20, 20)
            py = random.randint(-50, 30)
            p.drawEllipse(px, py, 5, 5)

    def draw_placeholder(self, p):
        p.setBrush(Qt.GlobalColor.magenta)
        p.drawRoundedRect(-70, -70, 140, 140, 12, 12)
