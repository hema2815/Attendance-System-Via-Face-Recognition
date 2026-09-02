import customtkinter as ctk
from config import COLORS, FONT_FAMILY, APP_TITLE, APP_SIZE, APP_MIN_SIZE, load_settings
from utils.threading_utils import EventBus
from core.camera import CameraThread
from core.face_engine import FaceEngine
from core.attendance import AttendanceSession
from core.student_manager import StudentManager
from ui.widgets.sidebar import Sidebar
from ui.widgets.status_bar import StatusBar
from ui.dashboard import DashboardScreen
from ui.registration import RegistrationScreen
from ui.attendance_viewer import AttendanceViewerScreen
from ui.settings import SettingsScreen


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_TITLE)
        self.geometry(APP_SIZE)
        self.minsize(*APP_MIN_SIZE)

        self.settings = load_settings()
        ctk.set_appearance_mode(self.settings.get("appearance_mode", "dark"))
        ctk.set_default_color_theme("blue")

        self.event_bus = EventBus(self)
        self.face_engine = FaceEngine()
        self.face_engine.load_model()
        self.attendance_session = AttendanceSession()
        self.student_manager = StudentManager(self.face_engine)

        source = self.settings.get("camera_index", 0)
        if self.settings.get("camera_source") == "ip":
            source = self.settings.get("camera_url", "")
        self.camera = CameraThread(source=source, event_bus=self.event_bus)
        self.camera.start()

        self.grid_columnconfigure(0, minsize=240)
        self.grid_columnconfigure(1, weight=0, minsize=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self, self)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")

        divider = ctk.CTkFrame(self, width=1, fg_color=COLORS["border"], corner_radius=0)
        divider.grid(row=0, column=1, rowspan=2, sticky="ns")

        self._content = ctk.CTkFrame(self, fg_color=COLORS["bg_main"], corner_radius=0)
        self._content.grid(row=0, column=2, sticky="nsew")
        self._content.grid_columnconfigure(0, weight=1)
        self._content.grid_rowconfigure(0, weight=1)

        self.status_bar = StatusBar(self, self)
        self.status_bar.grid(row=1, column=2, sticky="ew")

        self.status_bar.update_model(self.face_engine.is_loaded, self.face_engine.student_count)

        self._screens = {
            "dashboard": DashboardScreen,
            "register": RegistrationScreen,
            "attendance": AttendanceViewerScreen,
            "settings": SettingsScreen,
        }
        self._current_screen = None
        self._current_screen_name = None

        self.show_screen("dashboard")

        self.event_bus.subscribe("camera_connected", lambda _: self.status_bar.update_camera(True))
        self.event_bus.subscribe("camera_disconnected", lambda _: self.status_bar.update_camera(False))

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def show_screen(self, name):
        if name == self._current_screen_name:
            return

        if self._current_screen is not None:
            if hasattr(self._current_screen, "on_hide"):
                self._current_screen.on_hide()
            self._current_screen.destroy()

        screen_class = self._screens.get(name)
        if screen_class is None:
            return

        self._current_screen = screen_class(self._content, self)
        self._current_screen.grid(row=0, column=0, sticky="nsew")
        self._current_screen_name = name

        if hasattr(self._current_screen, "on_show"):
            self._current_screen.on_show()

        self.sidebar.set_active(name)

    def _on_close(self):
        if self.attendance_session.is_active:
            self.attendance_session.stop()
        self.camera.stop()
        self.destroy()
