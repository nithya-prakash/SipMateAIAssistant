from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QFont, QPolygon
from PySide6.QtCore import Qt, QPoint, QRectF
from characters.character import Character

class VectorRenderer(QWidget):
    """
    Renders procedural characters using QPainter.
    This fulfills CRITICAL REQUIREMENT 3: Character Pipeline placeholders.
    """
    def __init__(self, character: Character, parent=None):
        super().__init__(parent)
        self.character = character
        self.setFixedSize(100, 100) # Fixed logical size for the character bounding box
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if self.character.id == "airplane":
            self._draw_airplane(painter)
        elif self.character.id == "cat":
            self._draw_cat(painter)
        else:
            self._draw_default(painter)
            
    def _draw_airplane(self, painter: QPainter):
        # Draw a simple vector airplane
        painter.setBrush(QColor(200, 200, 200))
        painter.setPen(Qt.PenStyle.NoPen)
        
        # Fuselage
        painter.drawEllipse(20, 40, 60, 20)
        # Wings
        polygon = QPolygon([
            QPoint(50, 40),
            QPoint(30, 10),
            QPoint(40, 10),
            QPoint(60, 40)
        ])
        painter.drawPolygon(polygon)
        
        # Tail
        tail = QPolygon([
            QPoint(25, 45),
            QPoint(10, 25),
            QPoint(20, 25),
            QPoint(35, 45)
        ])
        painter.drawPolygon(tail)
        
        # Window
        painter.setBrush(QColor(100, 200, 255))
        painter.drawEllipse(65, 45, 8, 8)

    def _draw_cat(self, painter: QPainter):
        # Draw a simple vector cat head
        painter.setBrush(QColor(255, 165, 0)) # Orange cat
        painter.setPen(Qt.PenStyle.NoPen)
        
        # Head
        painter.drawEllipse(25, 30, 50, 40)
        # Ears
        ears = QPolygon([
            QPoint(30, 35), QPoint(25, 10), QPoint(45, 30),
            QPoint(55, 30), QPoint(75, 10), QPoint(70, 35)
        ])
        painter.drawPolygon(ears)
        
        # Eyes
        painter.setBrush(QColor(0, 0, 0))
        painter.drawEllipse(35, 45, 5, 5)
        painter.drawEllipse(60, 45, 5, 5)
        
    def _draw_default(self, painter: QPainter):
        painter.setBrush(QColor(100, 100, 255))
        painter.drawEllipse(10, 10, 80, 80)
