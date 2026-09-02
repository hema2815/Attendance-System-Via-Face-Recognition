# FaceAttend - Smart Attendance System

A real-time face recognition attendance system with a modern desktop GUI. Uses DeepFace for face embedding extraction and an SVM classifier for identity recognition. Built with CustomTkinter for a sleek dark-themed interface.

## Features

- **Face Registration** - Capture photos via webcam with real-time face detection
- **Image Augmentation** - OpenCV-based augmentation (rotation, shift, zoom, flip, brightness) for robust training
- **Face Embedding Extraction** - DeepFace with the Facenet model
- **SVM Classification** - scikit-learn SVM for identity recognition with confidence scoring
- **Real-time Recognition** - Live webcam feed with face detection overlays
- **Attendance Sessions** - Start/stop sessions, auto-mark attendance with duplicate prevention
- **Excel Export** - Formatted attendance reports exported to `.xlsx`
- **Settings Panel** - Configurable camera source (USB/IP), confidence threshold, recognition interval, and appearance mode

## Requirements

- Python 3.10+
- Webcam (USB or IP camera)

## Installation

```bash
# Create a virtual environment (use a short path on Windows to avoid long-path issues with TensorFlow)
python -m venv D:\venvs\faceattend

# Activate the virtual environment
# Windows PowerShell:
D:\venvs\faceattend\Scripts\Activate.ps1
# Windows CMD:
D:\venvs\faceattend\Scripts\activate.bat
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

### Workflow

1. **Register Students** - Navigate to "Register Student", enter name and ID, capture 5 photos
2. **Train Model** - Happens automatically after registration
3. **Start Session** - Go to Dashboard, click "Start Session" to begin attendance tracking
4. **View Records** - Check "Attendance Log" for current and past session records
5. **Export** - Sessions are auto-exported to Excel when stopped

## Project Structure

```
project/
├── main.py                  # Entry point
├── config.py                # Settings, paths, colors, fonts
├── requirements.txt         # Python dependencies
├── core/
│   ├── face_engine.py       # DeepFace embedding + SVM training/recognition
│   ├── camera.py            # Threaded camera capture
│   ├── attendance.py        # Session management + attendance marking
│   └── student_manager.py   # Student registration + deletion
├── ui/
│   ├── app.py               # Main application window
│   ├── dashboard.py         # Live camera feed + session controls
│   ├── registration.py      # Student registration form
│   ├── attendance_viewer.py # Attendance records table
│   ├── settings.py          # Camera, recognition, appearance settings
│   └── widgets/
│       ├── sidebar.py       # Navigation sidebar
│       ├── camera_preview.py # Camera feed widget
│       └── status_bar.py    # Bottom status bar
├── utils/
│   ├── image_utils.py       # Augmentation, resizing, drawing utilities
│   ├── excel_export.py      # Formatted Excel report generation
│   └── threading_utils.py   # Event bus for cross-thread communication
└── data/                    # Auto-created at runtime
    ├── faces/               # Registered student face images
    ├── models/              # Trained SVM model + label dictionary
    └── attendance_records/  # Exported Excel attendance reports
```

## Configuration

Settings are saved to `data/settings.json` and can be adjusted from the Settings screen:

| Setting | Default | Description |
|---------|---------|-------------|
| Camera Source | USB (index 0) | USB webcam or IP camera (RTSP/HTTP) |
| Confidence Threshold | 60% | Minimum confidence for attendance marking |
| Recognition Interval | 500ms | Time between recognition attempts |
| Appearance Mode | Dark | Dark, Light, or System |

## Author

Muhammad Muzammil
[BlackAlpha-debug](https://github.com/BlackAlpha-debug)
