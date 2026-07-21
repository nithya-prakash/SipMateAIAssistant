from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QPainterPath
from PySide6.QtCore import Qt, QTimer
import math
import random

class AnimatedVectorWidget(QWidget):
    def __init__(self, character_id, parent=None):
        super().__init__(parent)
        self.character_id = character_id
        self.setFixedSize(140, 140)
        
        self.tick = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(50) # 20 FPS

    def update_animation(self):
        self.tick += 1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Dispatch to specific drawing function
        func = getattr(self, f"draw_{self.character_id}", self.draw_placeholder)
        func(painter)
        painter.end()

    def draw_airplane(self, p):
        p.translate(70, 70)
        p.rotate(15 * math.sin(self.tick * 0.1))
        
        # Smoke
        if self.tick % 4 < 2:
            p.setBrush(QColor(200, 200, 200, 150))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(-80, 0, 15, 15)
            p.drawEllipse(-100, 5, 10, 10)
            
        p.setBrush(QColor(50, 150, 250))
        p.drawRoundedRect(-40, -15, 80, 30, 10, 10)
        p.setBrush(QColor(200, 200, 200))
        p.drawRect(-10, -35, 20, 20)
        # Propeller
        p.rotate(self.tick * 20)
        p.setBrush(QColor(100, 100, 100))
        p.drawEllipse(35, -20, 10, 40)

    def draw_cat(self, p):
        y_offset = math.sin(self.tick * 0.3) * 5
        p.translate(70, 70 + y_offset)
        
        tail_rot = math.sin(self.tick * 0.2) * 20
        p.save()
        p.translate(-30, 0)
        p.rotate(tail_rot)
        p.setBrush(QColor(255, 150, 50))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(-20, -5, 30, 10)
        p.restore()
        
        p.setBrush(QColor(255, 150, 50))
        p.drawEllipse(-30, -20, 60, 40)
        p.drawEllipse(10, -40, 30, 30)
        
        path = QPainterPath()
        path.moveTo(15, -35)
        path.lineTo(20, -55)
        path.lineTo(30, -35)
        p.drawPath(path)
        
        p.setBrush(QColor(0, 0, 0))
        if self.tick % 40 < 3:
            p.drawRect(20, -30, 5, 2)
            p.drawRect(30, -30, 5, 2)
        else:
            p.drawEllipse(20, -32, 5, 5)
            p.drawEllipse(30, -32, 5, 5)
            
    def draw_dog(self, p):
        y_offset = math.sin(self.tick * 0.4) * 8 
        p.translate(70, 70 + y_offset)
        
        tail_rot = math.sin(self.tick * 0.8) * 30
        p.save()
        p.translate(-30, 0)
        p.rotate(tail_rot)
        p.setBrush(QColor(139, 69, 19))
        p.drawEllipse(-20, -5, 30, 15)
        p.restore()
        
        p.setBrush(QColor(160, 82, 45))
        p.drawEllipse(-30, -20, 60, 40)
        p.drawEllipse(10, -35, 35, 35)
        
        p.setBrush(QColor(100, 50, 10))
        p.drawEllipse(15, -25, 10, 25)
        
        p.setBrush(Qt.GlobalColor.black)
        p.drawEllipse(35, -25, 5, 5)
        
        p.setBrush(QColor(100, 200, 255))
        p.drawRect(40, -15, 20, 10)

    def draw_girl(self, p):
        p.translate(70, 70)
        
        p.setBrush(QColor(150, 100, 200))
        p.drawEllipse(-15, -10, 30, 50)
        
        p.setBrush(QColor(255, 220, 177))
        p.drawEllipse(-20, -50, 40, 40)
        
        p.setBrush(QColor(50, 30, 10))
        path = QPainterPath()
        path.addEllipse(-22, -52, 44, 25)
        p.drawPath(path)
        
        arm_rot = math.sin(self.tick * 0.2) * 30 if self.tick % 60 < 30 else 0
        p.save()
        p.translate(15, -5)
        p.rotate(arm_rot - 45)
        p.setBrush(QColor(255, 220, 177))
        p.drawEllipse(0, 0, 25, 8)
        p.restore()
        
        p.setBrush(QColor(100, 200, 255))
        p.drawRect(-25, -20, 10, 20)
        
    def draw_rocket(self, p):
        p.translate(70, 70)
        y_shake = math.sin(self.tick) * 2
        p.translate(0, y_shake)
        
        if self.tick % 2 == 0:
            p.setBrush(QColor(255, 100, 0))
            p.drawEllipse(-15, 30, 30, 40)
            p.setBrush(QColor(255, 200, 0))
            p.drawEllipse(-10, 30, 20, 25)
            
        p.setBrush(QColor(200, 200, 200))
        p.drawEllipse(-20, -40, 40, 80)
        
        p.setBrush(QColor(100, 200, 255))
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
        p.translate(70, 70)
        
        if self.tick % 50 == 0:
            p.translate(random.randint(-5, 5), random.randint(-5, 5))
            
        p.setBrush(QColor(150, 160, 170))
        p.drawRect(-25, -20, 50, 50)
        
        p.drawRect(-30, -70, 60, 50)
        
        p.drawLine(0, -70, 0, -90)
        p.setBrush(QColor(255, 0, 0) if self.tick % 10 < 5 else QColor(100, 0, 0))
        p.drawEllipse(-5, -95, 10, 10)
        
        p.setBrush(QColor(0, 255, 255))
        p.drawRect(-20, -55, 15, 10)
        p.drawRect(5, -55, 15, 10)

    def draw_penguin(self, p):
        p.translate(70, 70)
        rot = math.sin(self.tick * 0.3) * 10
        p.rotate(rot)
        
        p.setBrush(QColor(0, 0, 0))
        p.drawEllipse(-25, -40, 50, 80)
        
        p.setBrush(QColor(255, 255, 255))
        p.drawEllipse(-15, -20, 30, 50)
        
        p.setBrush(QColor(255, 150, 0))
        path = QPainterPath()
        path.moveTo(-5, -30)
        path.lineTo(5, -30)
        path.lineTo(0, -20)
        p.drawPath(path)

    def draw_panda(self, p):
        p.translate(70, 70)
        
        p.setBrush(Qt.GlobalColor.black)
        p.drawEllipse(-35, -45, 20, 20)
        p.drawEllipse(15, -45, 20, 20)
        
        p.setBrush(Qt.GlobalColor.white)
        p.drawEllipse(-40, -40, 80, 70)
        
        p.setBrush(Qt.GlobalColor.black)
        p.drawEllipse(-25, -20, 20, 25)
        p.drawEllipse(5, -20, 20, 25)
        
        p.setBrush(Qt.GlobalColor.white)
        p.drawEllipse(-20, -15, 8, 8)
        p.drawEllipse(10, -15, 8, 8)

    def draw_butterfly(self, p):
        p.translate(70, 70)
        y_offset = math.sin(self.tick * 0.2) * 10
        p.translate(0, y_offset)
        
        wing_scale = math.sin(self.tick * 0.5) * 0.5 + 0.5
        
        p.setBrush(QColor(255, 100, 200))
        p.drawEllipse(-30 * wing_scale, -20, 30 * wing_scale, 40)
        p.drawEllipse(0, -20, 30 * wing_scale, 40)
        
        p.setBrush(QColor(50, 50, 50))
        p.drawEllipse(-5, -30, 10, 60)

    def draw_ghost(self, p):
        p.translate(70, 70)
        y_offset = math.sin(self.tick * 0.1) * 15
        p.translate(0, y_offset)
        
        alpha = int(200 + math.sin(self.tick * 0.05) * 50)
        p.setBrush(QColor(240, 240, 255, alpha))
        p.setPen(Qt.PenStyle.NoPen)
        
        path = QPainterPath()
        path.moveTo(-30, 40)
        path.lineTo(-30, -20)
        path.arcTo(-30, -50, 60, 60, 180, -180)
        path.lineTo(30, 40)
        for i in range(3):
            path.quadTo(20 - i*20, 50, 10 - i*20, 40)
            
        p.drawPath(path)
        
        p.setBrush(QColor(0, 0, 0, alpha))
        p.drawEllipse(-15, -20, 10, 15)
        p.drawEllipse(5, -20, 10, 15)
        p.drawEllipse(-5, 0, 10, 10)

    def draw_cow(self, p):
        p.translate(70, 70)
        y_offset = math.sin(self.tick * 0.2) * 3
        p.translate(0, y_offset)
        
        p.setBrush(Qt.GlobalColor.white)
        p.drawRect(-40, -20, 80, 50)
        
        p.setBrush(Qt.GlobalColor.black)
        p.drawEllipse(-30, -10, 20, 20)
        p.drawEllipse(10, 0, 25, 20)
        
        p.setBrush(Qt.GlobalColor.white)
        p.drawEllipse(20, -35, 30, 30)
        
        chew = math.sin(self.tick * 0.5) * 2
        p.setBrush(QColor(255, 180, 180))
        p.drawEllipse(35, -25 + chew, 15, 20)

    def draw_wizard(self, p):
        p.translate(70, 70)
        p.setBrush(QColor(100, 50, 200))
        
        p.drawRect(-20, -10, 40, 50)
        
        path = QPainterPath()
        path.moveTo(-30, -30)
        path.lineTo(30, -30)
        path.lineTo(0, -80)
        p.drawPath(path)
        
        p.setBrush(QColor(255, 200, 150))
        p.drawEllipse(-15, -30, 30, 25)
        
        p.setBrush(QColor(220, 220, 220))
        path = QPainterPath()
        path.moveTo(-15, -15)
        path.lineTo(15, -15)
        path.lineTo(0, 10)
        p.drawPath(path)

    def draw_alien(self, p):
        p.translate(70, 70)
        p.translate(0, math.sin(self.tick * 0.1) * 10)
        
        p.setBrush(QColor(100, 100, 100))
        p.drawEllipse(-50, 10, 100, 30)
        
        p.setBrush(QColor(150, 255, 255, 150))
        p.drawEllipse(-30, -20, 60, 50)
        
        p.setBrush(QColor(50, 255, 50))
        p.drawEllipse(-15, -10, 30, 30)
        p.setBrush(Qt.GlobalColor.black)
        p.drawEllipse(-10, -5, 8, 12)
        p.drawEllipse(2, -5, 8, 12)

    def draw_dragon(self, p):
        p.translate(70, 70)
        p.translate(0, math.sin(self.tick * 0.3) * 10)
        
        p.setBrush(QColor(200, 50, 50))
        p.drawEllipse(-30, -20, 60, 40)
        p.drawEllipse(15, -40, 30, 30)
        
        if self.tick % 10 < 5:
            p.setBrush(QColor(255, 100, 0))
            path = QPainterPath()
            path.moveTo(40, -30)
            path.lineTo(80, -20)
            path.lineTo(80, -40)
            p.drawPath(path)

    def draw_eiffel_tower(self, p):
        p.translate(70, 70)
        p.setBrush(QColor(150, 150, 160))
        
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
            p.setBrush(QColor(255, 255, 200))
            px = random.randint(-20, 20)
            py = random.randint(-50, 30)
            p.drawEllipse(px, py, 5, 5)

    def draw_placeholder(self, p):
        p.setBrush(Qt.GlobalColor.magenta)
        p.drawRect(0, 0, 140, 140)
