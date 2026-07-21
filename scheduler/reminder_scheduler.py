from PySide6.QtCore import QObject, QTimer, Signal
from ai.adaptive_scheduler import AdaptiveScheduler

class ReminderScheduler(QObject):
    reminder_triggered = Signal()

    def __init__(self, adaptive_scheduler: AdaptiveScheduler, settings_manager, parent=None):
        super().__init__(parent)
        self.adaptive_scheduler = adaptive_scheduler
        self.settings_manager = settings_manager
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_timeout)
        
        # Listen for setting changes
        self.settings_manager.settings_changed.connect(self._on_settings_changed)
        
    def _on_settings_changed(self, settings):
        # Restart the timer with new settings
        self.start()
        
    def start(self):
        settings = self.settings_manager.settings
        if settings.paused:
            self.stop()
            return
            
        if settings.ai_adaptive_scheduling_enabled:
            # Retrain and get dynamic interval
            self.adaptive_scheduler.train_model()
            mins = self.adaptive_scheduler.get_next_optimal_reminder_minutes()
            interval_ms = mins * 60 * 1000
            import logging
            logging.info(f"Adaptive Scheduler: Next reminder in {mins} minutes.")
        else:
            interval_ms = settings.reminder_interval_minutes * 60 * 1000
            
        self.timer.start(interval_ms)
        
    def stop(self):
        self.timer.stop()
        
    def _on_timeout(self):
        self.reminder_triggered.emit()
        # Reschedule automatically using AI logic
        self.start()

    def trigger_now(self):
        self.reminder_triggered.emit()
