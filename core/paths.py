import os
from PySide6.QtCore import QStandardPaths

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Use macOS AppDataLocation (~/Library/Application Support/SipMate)
app_data = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
if not app_data:
    app_data = BASE_DIR
DATA_DIR = os.path.join(app_data, "SipMate")

try:
    os.makedirs(DATA_DIR, exist_ok=True)
except PermissionError:
    DATA_DIR = os.path.join(BASE_DIR, "data")
    os.makedirs(DATA_DIR, exist_ok=True)
