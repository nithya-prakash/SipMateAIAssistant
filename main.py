import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from ui.overlay_window import OverlayWindow
from system.tray import HydraTray
from scheduler.reminder_scheduler import ReminderScheduler
from ai.adaptive_scheduler import AdaptiveScheduler

def main():
    import logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    try:
        from AppKit import NSApp, NSApplicationActivationPolicyAccessory
        NSApp.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
    except ImportError:
        pass
    
    from tracker.hydration_tracker import HydrationTracker
    from core.settings_manager import SettingsManager
    from core.paths import DATA_DIR
    
    settings_manager = SettingsManager(DATA_DIR)
    tracker = HydrationTracker()
    overlay = OverlayWindow(tracker, settings_manager)
    tray = HydraTray(app, overlay, settings_manager)
    
    # Setup AI Scheduler
    adaptive_scheduler = AdaptiveScheduler(overlay.tracker)
    
    # Setup timer scheduler
    scheduler = ReminderScheduler(adaptive_scheduler, settings_manager, app)
    scheduler.reminder_triggered.connect(overlay.trigger_reminder)
    
    # Start scheduler
    scheduler.start()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
