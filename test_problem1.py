from core.settings_manager import SettingsManager
from core.paths import DATA_DIR
import os

print(f"DATA_DIR: {DATA_DIR}")
sm1 = SettingsManager(DATA_DIR)
sm1.update(ai_adaptive_scheduling_enabled=False, sound_enabled=False)

sm2 = SettingsManager(DATA_DIR)
assert sm2.settings.ai_adaptive_scheduling_enabled == False
assert sm2.settings.sound_enabled == False
print("Settings persistence verified successfully.")
