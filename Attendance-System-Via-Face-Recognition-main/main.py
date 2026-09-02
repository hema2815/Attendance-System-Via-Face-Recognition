import os
import sys

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import FACE_FOLDER, MODEL_FOLDER, ATTENDANCE_FOLDER

for folder in [FACE_FOLDER, MODEL_FOLDER, ATTENDANCE_FOLDER]:
    os.makedirs(folder, exist_ok=True)

from ui.app import App

if __name__ == "__main__":
    app = App()
    app.mainloop()
