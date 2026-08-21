import json
import os
from dataclasses import dataclass, asdict, field
from typing import List
from PySide6.QtCore import QObject, Signal

@dataclass
class Settings:
    ai_adaptive_scheduling_enabled: bool = True
    ai_dynamic_messages_enabled: bool = True
    sound_enabled: bool = True
    reminder_interval_minutes: int = 60
    working_hours_enabled: bool = False
    working_hours_start: int = 9
    working_hours_end: int = 17
    paused: bool = False
    dark_mode: bool = True

    # Character system: character_mode is one of "random", "single", "daily_rotation",
    # "favorites", "sipmate_originals", "princess_mode", "disney_favorites".
    character_mode: str = "random"
    selected_character_id: str = "dog"
    favorite_character_ids: List[str] = field(default_factory=list)

class SettingsManager(QObject):
    settings_changed = Signal(Settings)

    def __init__(self, data_dir: str):
        super().__init__()
        self.settings_file = os.path.join(data_dir, "settings.json")
        self.settings = Settings()
        self.load()

    def load(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r") as f:
                    data = json.load(f)
                    # Update fields that exist in data
                    for k, v in data.items():
                        if hasattr(self.settings, k):
                            setattr(self.settings, k, v)
            except Exception as e:
                import logging
                logging.error(f"Failed to load settings: {e}")
        else:
            self.save()

    def save(self):
        try:
            with open(self.settings_file, "w") as f:
                json.dump(asdict(self.settings), f, indent=4)
        except Exception as e:
            import logging
            logging.error(f"Failed to save settings: {e}")

    def update(self, **kwargs):
        changed = False
        for k, v in kwargs.items():
            if hasattr(self.settings, k) and getattr(self.settings, k) != v:
                setattr(self.settings, k, v)
                changed = True
        
        if changed:
            self.save()
            self.settings_changed.emit(self.settings)
