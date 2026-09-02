import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
FACE_FOLDER = os.path.join(DATA_DIR, "faces")
MODEL_FOLDER = os.path.join(DATA_DIR, "models")
ATTENDANCE_FOLDER = os.path.join(DATA_DIR, "attendance_records")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

SVM_MODEL_FILE = "svm_model.pkl"
LABEL_DICT_FILE = "label_dict.pkl"

DEEPFACE_MODEL = "Facenet"
TARGET_IMAGE_SIZE = (160, 160)
CONFIDENCE_THRESHOLD = 0.6
AUGMENTATION_COUNT = 3
CAPTURE_COUNT = 5
RECOGNITION_INTERVAL_MS = 500
DEFAULT_CAMERA_INDEX = 0

APP_TITLE = "FaceAttend - Smart Attendance System"
APP_SIZE = "1340x820"
APP_MIN_SIZE = (1100, 650)

COLORS = {
    "primary": "#6C63FF",
    "primary_hover": "#5A52D5",
    "primary_light": "#8B83FF",
    "success": "#00C853",
    "success_hover": "#00A844",
    "success_dim": "#1B3A2A",
    "danger": "#FF5252",
    "danger_hover": "#E04545",
    "danger_dim": "#3A1B1B",
    "warning": "#FFB74D",
    "warning_dim": "#3A2E1B",
    "info": "#29B6F6",

    "bg_main": "#0D1117",
    "bg_card": "#161B22",
    "bg_card_hover": "#1C2333",
    "bg_sidebar": "#0D1117",
    "bg_input": "#0D1117",
    "bg_elevated": "#21262D",
    "bg_table_header": "#1C2333",
    "bg_table_stripe": "#161B22",

    "text_primary": "#F0F6FC",
    "text_secondary": "#8B949E",
    "text_muted": "#484F58",
    "border": "#30363D",
    "border_light": "#21262D",
    "accent_glow": "#6C63FF20",
}

FONT_FAMILY = "Segoe UI"


def load_settings():
    defaults = {
        "camera_source": "usb",
        "camera_index": DEFAULT_CAMERA_INDEX,
        "camera_url": "",
        "confidence_threshold": CONFIDENCE_THRESHOLD,
        "recognition_interval": RECOGNITION_INTERVAL_MS,
        "appearance_mode": "dark",
    }
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                saved = json.load(f)
            defaults.update(saved)
        except (json.JSONDecodeError, IOError):
            pass
    return defaults


def save_settings(settings):
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)
