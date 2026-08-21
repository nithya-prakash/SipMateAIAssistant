from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QAction
from PySide6.QtCore import Qt, QObject
from ui.settings_window import SettingsWindow
from ui.insights_window import InsightsWindow
from ui.character_collection_window import CharacterCollectionWindow

class HydraTray(QObject):
    def __init__(self, app, overlay_window, settings_manager):
        super().__init__()
        self.app = app
        self.overlay_window = overlay_window
        self.settings_manager = settings_manager

        self.settings_window = SettingsWindow(self.settings_manager)
        self.insights_window = InsightsWindow(self.overlay_window.tracker)
        self.character_collection_window = CharacterCollectionWindow(self.settings_manager)
        
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(self.create_placeholder_icon())
        
        self.menu = QMenu()
        
        self.action_test = QAction("Test Overlay")
        self.action_test.triggered.connect(self.overlay_window.show_safe_overlay)
        self.menu.addAction(self.action_test)
        
        self.menu.addSeparator()
        
        self.action_insights = QAction("AI Insights Dashboard")
        self.action_insights.triggered.connect(self.insights_window.show)
        self.menu.addAction(self.action_insights)

        self.action_characters = QAction("Character Collection")
        self.action_characters.triggered.connect(self.character_collection_window.show)
        self.menu.addAction(self.action_characters)

        self.action_settings = QAction("Settings")
        self.action_settings.triggered.connect(self.settings_window.show)
        self.menu.addAction(self.action_settings)
        
        self.menu.addSeparator()
        
        self.action_quit = QAction("Quit Hydra")
        self.action_quit.triggered.connect(self.app.quit)
        self.menu.addAction(self.action_quit)
        
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.show()

    def create_placeholder_icon(self):
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.setBrush(QColor(0, 150, 255))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(4, 4, 24, 24)
        
        painter.setBrush(QColor(255, 255, 255, 200))
        painter.drawEllipse(8, 8, 8, 8)
        
        painter.end()
        return QIcon(pixmap)
