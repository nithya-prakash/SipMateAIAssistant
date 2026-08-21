import math
import random
from PySide6.QtCore import QPropertyAnimation, QPoint, QEasingCurve
from PySide6.QtWidgets import QWidget

# Horizontal travelers: enter from a randomly chosen side, rest near center for the
# interaction, then keep going in that same direction and leave from the OTHER side -
# a real crossing, not a peek-in-and-retreat.
_CROSSING_BEHAVIORS = ("fly_across", "walk_across", "walk_to_center", "float")


class AnimationBehaviors:
    @staticmethod
    def _wave_path(anim, start: QPoint, end: QPoint, base_y: int, amplitude: float, cycles: float,
                    samples: int = 12, curve=QEasingCurve.Type.InOutSine):
        """Lay down keyframes tracing a horizontal path with a rhythmic vertical bob,
        so movement reads as flying/walking instead of a flat linear slide."""
        anim.setEasingCurve(curve)
        for i in range(samples + 1):
            t = i / samples
            x = start.x() + (end.x() - start.x()) * t
            # Rectified sine gives a bouncy "step" cadence rather than a smooth up/down wobble
            y = base_y - abs(math.sin(t * math.pi * cycles)) * amplitude
            anim.setKeyValueAt(t, QPoint(int(x), int(y)))

    @staticmethod
    def _pick_crossing(geom, window):
        """Choose a random entry side, a shared rest x near the middle of the screen,
        and the exit x on the far side - so entrance and exit agree on one direction
        of travel all the way across."""
        margin = 60
        off_left = geom.x() - window.width() - margin
        off_right = geom.x() + geom.width() + margin
        rest_x = geom.x() + geom.width() // 2 - window.width() // 2
        if random.random() < 0.5:
            return off_left, rest_x, off_right, 1
        return off_right, rest_x, off_left, -1

    @staticmethod
    def setup_entrance(window: QWidget, character, geom):
        behavior = character.movement_style
        anim = QPropertyAnimation(window, b"pos")

        target_y = geom.y() + (geom.height() - window.height()) // 2

        if behavior in _CROSSING_BEHAVIORS:
            start_x, rest_x, exit_x, direction = AnimationBehaviors._pick_crossing(geom, window)
            window._exit_x = exit_x
            window._exit_dir = direction
        else:
            window._exit_x = None
            window._exit_dir = 0

        if behavior == "fly_across":
            start = QPoint(start_x, target_y)
            end = QPoint(rest_x, target_y)
            anim.setDuration(2200)
            AnimationBehaviors._wave_path(anim, start, end, target_y, amplitude=18, cycles=2.5)

        elif behavior == "walk_across":
            start = QPoint(start_x, target_y)
            end = QPoint(rest_x, target_y)
            anim.setDuration(3000)
            AnimationBehaviors._wave_path(anim, start, end, target_y, amplitude=12, cycles=5,
                                           curve=QEasingCurve.Type.Linear)
            # Anticipation: a tiny coil backward and down before committing to the walk,
            # like gathering weight before a first step. "Backward" means toward start_x.
            coil_x = start.x() + (14 if direction > 0 else -14)
            anim.setKeyValueAt(0.025, QPoint(coil_x, target_y + 5))

        elif behavior == "walk_to_center":
            start = QPoint(start_x, target_y)
            end = QPoint(rest_x, target_y)
            anim.setDuration(2200)
            AnimationBehaviors._wave_path(anim, start, end, target_y, amplitude=8, cycles=3)

        elif behavior == "launch_upward":
            start_x2 = geom.x() + geom.width() - window.width() - 50
            start_y = geom.height() + 50
            anim.setDuration(1300)
            # Anticipation: compress down before the big push (a coiled spring), THEN
            # the sideways sway + wind-up hover, then the launch itself.
            anim.setKeyValueAt(0.0, QPoint(start_x2, start_y))
            anim.setKeyValueAt(0.09, QPoint(start_x2 + 3, start_y + 14))
            anim.setKeyValueAt(0.65, QPoint(start_x2 - 14, int(target_y + (start_y - target_y) * 0.18)))
            anim.setKeyValueAt(1.0, QPoint(start_x2, target_y))
            anim.setEasingCurve(QEasingCurve.Type.OutExpo)

        elif behavior in ("appear_center", "teleport"):
            start_x2 = geom.width() // 2 - window.width() // 2
            anim.setStartValue(QPoint(start_x2, target_y))
            anim.setEndValue(QPoint(start_x2, target_y))
            anim.setDuration(500)

        elif behavior == "float":
            start = QPoint(start_x, target_y + 90)
            mid = QPoint(start_x + (40 * direction), target_y - 15)
            end = QPoint(rest_x, target_y)
            anim.setDuration(2400)
            anim.setKeyValueAt(0.0, start)
            anim.setKeyValueAt(0.55, mid)  # gentle overshoot before settling
            anim.setKeyValueAt(1.0, end)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        else:
            start_x2 = geom.x() + geom.width() - window.width() - 50
            anim.setStartValue(QPoint(start_x2, target_y - 50))
            anim.setEndValue(QPoint(start_x2, target_y))
            anim.setDuration(1000)

        window.move(anim.startValue())
        return anim

    @staticmethod
    def setup_exit(window: QWidget, character, geom):
        behavior = character.movement_style
        anim = QPropertyAnimation(window, b"pos")
        anim.setDuration(1500)

        start_pos = window.pos()
        exit_x = getattr(window, "_exit_x", None)

        if behavior == "launch_upward":
            end_pos = QPoint(start_pos.x(), -window.height() - 50)
            # Tiny anticipation dip down before the rocket commits upward
            anim.setKeyValueAt(0.0, start_pos)
            anim.setKeyValueAt(0.12, QPoint(start_pos.x(), start_pos.y() + 12))
            anim.setKeyValueAt(1.0, end_pos)
            anim.setEasingCurve(QEasingCurve.Type.InExpo)

        elif behavior in _CROSSING_BEHAVIORS and exit_x is not None:
            end = QPoint(exit_x, start_pos.y())
            cycles = 2.5 if behavior in ("fly_across", "float") else 3
            amplitude = 14 if behavior != "float" else 10
            AnimationBehaviors._wave_path(anim, start_pos, end, start_pos.y(), amplitude=amplitude,
                                           cycles=cycles, curve=QEasingCurve.Type.InSine)

        else:
            end_pos = QPoint(start_pos.x(), geom.height() + 50)
            anim.setStartValue(start_pos)
            anim.setEndValue(end_pos)
            anim.setEasingCurve(QEasingCurve.Type.InBack)

        return anim
