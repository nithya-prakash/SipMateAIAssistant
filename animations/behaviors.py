from PySide6.QtCore import QPropertyAnimation, QPoint, QEasingCurve
from PySide6.QtWidgets import QWidget

class AnimationBehaviors:
    @staticmethod
    def setup_entrance(window: QWidget, character, geom):
        behavior = character.movement_style
        anim = QPropertyAnimation(window, b"pos")
        anim.setDuration(1500)
        
        target_y = (geom.height() - window.height()) // 2
        
        if behavior == "fly_across":
            start_x = geom.x() - window.width() - 50
            end_x = geom.width() - window.width() - 50
            anim.setStartValue(QPoint(start_x, target_y))
            anim.setEndValue(QPoint(end_x, target_y))
            anim.setEasingCurve(QEasingCurve.Type.OutBack)
            
        elif behavior == "walk_across":
            start_x = geom.width() + 50
            end_x = geom.width() - window.width() - 50
            anim.setStartValue(QPoint(start_x, target_y))
            anim.setEndValue(QPoint(end_x, target_y))
            anim.setEasingCurve(QEasingCurve.Type.Linear)
            anim.setDuration(2500)
            
        elif behavior == "walk_to_center":
            start_x = geom.x() - window.width() - 50
            end_x = geom.width() // 2 - window.width() // 2
            anim.setStartValue(QPoint(start_x, target_y))
            anim.setEndValue(QPoint(end_x, target_y))
            anim.setEasingCurve(QEasingCurve.Type.OutSine)
            anim.setDuration(2000)
            
        elif behavior == "launch_upward":
            start_x = geom.width() - window.width() - 50
            start_y = geom.height() + 50
            anim.setStartValue(QPoint(start_x, start_y))
            anim.setEndValue(QPoint(start_x, target_y))
            anim.setEasingCurve(QEasingCurve.Type.OutExp)
            anim.setDuration(1000)
            
        elif behavior in ["appear_center", "teleport"]:
            start_x = geom.width() // 2 - window.width() // 2
            anim.setStartValue(QPoint(start_x, target_y))
            anim.setEndValue(QPoint(start_x, target_y))
            anim.setDuration(500)
            
        elif behavior == "float":
            start_x = geom.width() - window.width() - 50
            start_y = target_y + 100
            anim.setStartValue(QPoint(start_x, start_y))
            anim.setEndValue(QPoint(start_x, target_y))
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim.setDuration(2000)
        else:
            start_x = geom.width() - window.width() - 50
            anim.setStartValue(QPoint(start_x, target_y - 50))
            anim.setEndValue(QPoint(start_x, target_y))
            anim.setDuration(1000)

        window.move(anim.startValue())
        return anim

    @staticmethod
    def setup_exit(window: QWidget, character, geom):
        behavior = character.movement_style
        anim = QPropertyAnimation(window, b"pos")
        anim.setDuration(1500)
        
        start_pos = window.pos()
        
        if behavior == "launch_upward":
            end_pos = QPoint(start_pos.x(), -window.height() - 50)
            anim.setEasingCurve(QEasingCurve.Type.InExp)
        elif behavior == "fly_across" or behavior == "walk_across":
            end_pos = QPoint(geom.width() + 50, start_pos.y())
            anim.setEasingCurve(QEasingCurve.Type.InBack)
        elif behavior == "walk_to_center":
            end_pos = QPoint(geom.width() + 50, start_pos.y())
            anim.setEasingCurve(QEasingCurve.Type.InSine)
        else:
            end_pos = QPoint(start_pos.x(), geom.height() + 50)
            anim.setEasingCurve(QEasingCurve.Type.InBack)
            
        anim.setStartValue(start_pos)
        anim.setEndValue(end_pos)
        return anim
