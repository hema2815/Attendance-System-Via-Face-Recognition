import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import customtkinter as ctk
from config import COLORS, FONT_FAMILY
from utils.image_utils import draw_face_boxes
from ui.widgets.camera_preview import CameraPreview


class DashboardScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self._app = app
        self._detections = []
        self._recognition_running = False
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._recognition_busy = False

        self.grid_columnconfigure(0, weight=7)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(1, weight=1)

        # ── Header ──
        header = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header.grid(row=0, column=0, columnspan=2, padx=20, pady=(16, 0), sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header, text="Dashboard",
            font=ctk.CTkFont(family=FONT_FAMILY, size=24, weight="bold"),
            text_color=COLORS["text_primary"],
        ).grid(row=0, column=0, sticky="w")

        self._time_label = ctk.CTkLabel(
            header, text="",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            text_color=COLORS["text_muted"],
        )
        self._time_label.grid(row=0, column=2, sticky="e")

        # ── Left: Camera Feed ──
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=1, column=0, padx=(20, 8), pady=(12, 20), sticky="nsew")
        left.grid_rowconfigure(0, weight=1)
        left.grid_columnconfigure(0, weight=1)

        self._preview = CameraPreview(left, app.camera, size=(720, 480), overlay_fn=self._overlay)
        self._preview.grid(row=0, column=0, sticky="nsew")

        # ── Right Panel ──
        right = ctk.CTkFrame(self, fg_color="transparent", width=320)
        right.grid(row=1, column=1, padx=(8, 20), pady=(12, 20), sticky="nsew")
        right.grid_rowconfigure(4, weight=1)
        right.grid_columnconfigure(0, weight=1)

        # Session Card
        session_card = ctk.CTkFrame(right, fg_color=COLORS["bg_card"], corner_radius=14,
                                     border_width=1, border_color=COLORS["border"])
        session_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        session_card.grid_columnconfigure(0, weight=1)

        card_header = ctk.CTkFrame(session_card, fg_color="transparent")
        card_header.grid(row=0, column=0, padx=16, pady=(14, 4), sticky="ew")
        card_header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            card_header, text="Session Control",
            font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"),
            text_color=COLORS["text_primary"],
        ).grid(row=0, column=0, sticky="w")

        self._session_badge = ctk.CTkLabel(
            card_header, text=" INACTIVE ",
            font=ctk.CTkFont(family=FONT_FAMILY, size=10, weight="bold"),
            text_color=COLORS["text_muted"],
            fg_color=COLORS["bg_elevated"], corner_radius=6,
        )
        self._session_badge.grid(row=0, column=1, sticky="e")

        stats_frame = ctk.CTkFrame(session_card, fg_color="transparent")
        stats_frame.grid(row=1, column=0, padx=16, pady=(4, 4), sticky="ew")
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self._duration_val = self._make_stat(stats_frame, "Duration", "00:00:00", 0)
        self._count_val = self._make_stat(stats_frame, "Present", "0", 1)
        self._conf_val = self._make_stat(stats_frame, "Threshold", f"{self._app.settings.get('confidence_threshold', 0.6):.0%}", 2)

        btn_frame = ctk.CTkFrame(session_card, fg_color="transparent")
        btn_frame.grid(row=2, column=0, padx=16, pady=(6, 14), sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        self._start_btn = ctk.CTkButton(
            btn_frame, text="Start Session", height=38,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            fg_color=COLORS["success"], hover_color=COLORS["success_hover"],
            corner_radius=10, command=self._start_session,
        )
        self._start_btn.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        self._stop_btn = ctk.CTkButton(
            btn_frame, text="Stop Session", height=38,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            fg_color=COLORS["bg_elevated"], hover_color=COLORS["danger_hover"],
            text_color=COLORS["text_secondary"],
            corner_radius=10, state="disabled", command=self._stop_session,
        )
        self._stop_btn.grid(row=0, column=1, padx=(4, 0), sticky="ew")

        # Warning if no model
        if not app.face_engine.is_loaded:
            warn = ctk.CTkFrame(right, fg_color=COLORS["warning_dim"], corner_radius=10,
                                border_width=1, border_color="#4D3A1B")
            warn.grid(row=1, column=0, sticky="ew", pady=(0, 10))
            ctk.CTkLabel(
                warn, text="No trained model found. Register\nstudents first to enable recognition.",
                font=ctk.CTkFont(family=FONT_FAMILY, size=12),
                text_color=COLORS["warning"], justify="left",
            ).pack(padx=14, pady=12, anchor="w")

        # Attendance Feed Header
        feed_header = ctk.CTkFrame(right, fg_color="transparent")
        feed_header.grid(row=2, column=0, sticky="ew", pady=(4, 6))
        feed_header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            feed_header, text="Live Attendance",
            font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"),
            text_color=COLORS["text_primary"],
        ).grid(row=0, column=0, sticky="w")

        self._feed_count = ctk.CTkLabel(
            feed_header, text="0 entries",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=COLORS["text_muted"],
        )
        self._feed_count.grid(row=0, column=1, sticky="e")

        # Attendance List
        self._attendance_list = ctk.CTkScrollableFrame(
            right, fg_color=COLORS["bg_card"], corner_radius=14,
            border_width=1, border_color=COLORS["border"],
            scrollbar_button_color=COLORS["bg_elevated"],
            scrollbar_button_hover_color=COLORS["primary"],
        )
        self._attendance_list.grid(row=4, column=0, sticky="nsew")
        self._attendance_list.grid_columnconfigure(0, weight=1)

        self._empty_label = ctk.CTkLabel(
            self._attendance_list,
            text="Start a session to begin\ntracking attendance",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            text_color=COLORS["text_muted"], justify="center",
        )
        self._empty_label.grid(row=0, column=0, pady=40)

    def _make_stat(self, parent, label, value, col):
        frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_elevated"], corner_radius=8, height=52)
        frame.grid(row=0, column=col, padx=3, sticky="ew")
        frame.grid_propagate(False)

        val_label = ctk.CTkLabel(
            frame, text=value,
            font=ctk.CTkFont(family=FONT_FAMILY, size=16, weight="bold"),
            text_color=COLORS["text_primary"],
        )
        val_label.place(relx=0.5, rely=0.35, anchor="center")

        ctk.CTkLabel(
            frame, text=label,
            font=ctk.CTkFont(family=FONT_FAMILY, size=9),
            text_color=COLORS["text_muted"],
        ).place(relx=0.5, rely=0.72, anchor="center")

        return val_label

    def on_show(self):
        self._preview.start()
        self._recognition_running = True
        self._run_recognition()
        self._update_ui_loop()

    def on_hide(self):
        self._preview.stop()
        self._recognition_running = False

    def _overlay(self, frame):
        if self._detections:
            return draw_face_boxes(frame, self._detections)
        return frame

    def _run_recognition(self):
        if not self._recognition_running:
            return
        if not self._recognition_busy and self._app.face_engine.is_loaded:
            frame = self._app.camera.get_frame()
            if frame is not None:
                self._recognition_busy = True
                self._executor.submit(self._recognize_worker, frame)
        interval = self._app.settings.get("recognition_interval", 500)
        self.after(interval, self._run_recognition)

    def _recognize_worker(self, frame):
        try:
            results = self._app.face_engine.recognize_faces(frame)
            self._detections = results
            session = self._app.attendance_session
            if session.is_active:
                for det in results:
                    if session.mark_attendance(det["name"], det["confidence"]):
                        self.after(0, self._add_attendance_entry, det["name"], det["confidence"])
        except Exception:
            pass
        finally:
            self._recognition_busy = False

    def _update_ui_loop(self):
        if not self._recognition_running:
            return

        now = datetime.now()
        self._time_label.configure(text=now.strftime("%A, %B %d  •  %I:%M %p"))

        session = self._app.attendance_session
        if session.is_active:
            self._session_badge.configure(text=" ACTIVE ", fg_color=COLORS["success_dim"],
                                          text_color=COLORS["success"])
            self._duration_val.configure(text=session.duration)
            self._count_val.configure(text=str(session.count))
            self._app.status_bar.update_session(True, session.duration, session.count)
        else:
            self._session_badge.configure(text=" INACTIVE ", fg_color=COLORS["bg_elevated"],
                                          text_color=COLORS["text_muted"])
            self._app.status_bar.update_session(False)

        self._app.status_bar.update_camera(self._app.camera.is_connected)
        self.after(1000, self._update_ui_loop)

    def _start_session(self):
        if not self._app.face_engine.is_loaded:
            self._show_toast("Register students and train model first", COLORS["warning"])
            return
        self._app.attendance_session.start()
        self._start_btn.configure(state="disabled", fg_color=COLORS["bg_elevated"])
        self._stop_btn.configure(state="normal", fg_color=COLORS["danger"],
                                 text_color=COLORS["text_primary"])

        for w in self._attendance_list.winfo_children():
            w.destroy()
        self._empty_label = None
        self._feed_count.configure(text="0 entries")

    def _stop_session(self):
        filepath = self._app.attendance_session.stop()
        self._start_btn.configure(state="normal", fg_color=COLORS["success"])
        self._stop_btn.configure(state="disabled", fg_color=COLORS["bg_elevated"],
                                 text_color=COLORS["text_secondary"])
        self._detections = []
        if filepath:
            self._show_toast(f"Attendance saved to Excel", COLORS["success"])

    def _add_attendance_entry(self, name, confidence):
        if self._empty_label and self._empty_label.winfo_exists():
            self._empty_label.destroy()
            self._empty_label = None

        row_num = self._app.attendance_session.count
        self._feed_count.configure(text=f"{row_num} entries")

        entry = ctk.CTkFrame(self._attendance_list, fg_color=COLORS["bg_elevated"],
                              corner_radius=10, height=44)
        entry.grid(row=row_num, column=0, sticky="ew", padx=6, pady=3)
        entry.grid_columnconfigure(1, weight=1)
        entry.grid_propagate(False)

        num_badge = ctk.CTkLabel(
            entry, text=str(row_num), width=28, height=28,
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            fg_color=COLORS["primary"], corner_radius=14,
            text_color="#FFFFFF",
        )
        num_badge.grid(row=0, column=0, padx=(10, 8), pady=8)

        info = ctk.CTkFrame(entry, fg_color="transparent")
        info.grid(row=0, column=1, sticky="w", pady=4)

        ctk.CTkLabel(
            info, text=name,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            text_color=COLORS["text_primary"], anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            info, text=datetime.now().strftime("%I:%M:%S %p"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=10),
            text_color=COLORS["text_muted"], anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            entry, text=f"{confidence:.0%}",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=COLORS["success"],
        ).grid(row=0, column=2, padx=(5, 14), pady=8)

    def _show_toast(self, message, color):
        toast = ctk.CTkFrame(self, fg_color=COLORS["bg_elevated"], corner_radius=12,
                              border_width=1, border_color=color)
        toast.place(relx=0.5, rely=0.93, anchor="center")
        ctk.CTkLabel(
            toast, text=f"  {message}  ",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=color,
        ).pack(padx=16, pady=10)
        self.after(3000, toast.destroy)
