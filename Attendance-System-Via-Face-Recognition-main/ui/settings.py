import os
import threading
import customtkinter as ctk
from config import COLORS, FONT_FAMILY, FACE_FOLDER, ATTENDANCE_FOLDER, load_settings, save_settings


class SettingsScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self._app = app

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ── Header ──
        ctk.CTkLabel(
            self, text="Settings",
            font=ctk.CTkFont(family=FONT_FAMILY, size=24, weight="bold"),
            text_color=COLORS["text_primary"],
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=(16, 0), sticky="w")

        # ── Left Column ──
        left = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                       scrollbar_button_color=COLORS["bg_elevated"])
        left.grid(row=1, column=0, padx=(20, 8), pady=(12, 20), sticky="nsew")
        left.grid_columnconfigure(0, weight=1)

        # Camera Card
        cam_card = self._card(left, "Camera Source")
        cam_card.pack(fill="x", pady=(0, 10))

        self._cam_source_var = ctk.StringVar(value=app.settings.get("camera_source", "usb"))

        ctk.CTkRadioButton(
            cam_card, text="USB Webcam", variable=self._cam_source_var, value="usb",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
        ).pack(padx=20, pady=(0, 4), anchor="w")

        idx_frame = ctk.CTkFrame(cam_card, fg_color="transparent")
        idx_frame.pack(padx=40, pady=(0, 10), anchor="w")
        ctk.CTkLabel(idx_frame, text="Camera Index:",
                     font=ctk.CTkFont(family=FONT_FAMILY, size=12),
                     text_color=COLORS["text_muted"]).pack(side="left")
        self._cam_index_entry = ctk.CTkEntry(
            idx_frame, width=60, height=32,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color=COLORS["bg_input"], border_color=COLORS["border"], corner_radius=8,
        )
        self._cam_index_entry.pack(side="left", padx=6)
        self._cam_index_entry.insert(0, str(app.settings.get("camera_index", 0)))

        ctk.CTkRadioButton(
            cam_card, text="IP Camera (RTSP / HTTP)", variable=self._cam_source_var, value="ip",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
        ).pack(padx=20, pady=(4, 4), anchor="w")

        self._cam_url_entry = ctk.CTkEntry(
            cam_card, height=36, placeholder_text="rtsp://user:pass@ip:port/stream",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color=COLORS["bg_input"], border_color=COLORS["border"], corner_radius=8,
        )
        self._cam_url_entry.pack(padx=40, pady=(0, 8), fill="x")
        url = app.settings.get("camera_url", "")
        if url:
            self._cam_url_entry.insert(0, url)

        apply_frame = ctk.CTkFrame(cam_card, fg_color="transparent")
        apply_frame.pack(padx=16, pady=(0, 14), fill="x")

        ctk.CTkButton(
            apply_frame, text="Apply Camera", height=36,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            corner_radius=10, command=self._apply_camera,
        ).pack(side="left")

        self._cam_status = ctk.CTkLabel(
            apply_frame, text="",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=COLORS["text_muted"],
        )
        self._cam_status.pack(side="left", padx=10)

        # Recognition Card
        recog_card = self._card(left, "Recognition")
        recog_card.pack(fill="x", pady=(0, 10))

        self._threshold_label = ctk.CTkLabel(
            recog_card,
            text=f"Confidence Threshold:  {app.settings.get('confidence_threshold', 0.6):.0%}",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            text_color=COLORS["text_secondary"],
        )
        self._threshold_label.pack(padx=20, anchor="w")

        self._threshold_slider = ctk.CTkSlider(
            recog_card, from_=0.3, to=0.95, number_of_steps=65,
            fg_color=COLORS["bg_elevated"], progress_color=COLORS["primary"],
            button_color=COLORS["primary"], button_hover_color=COLORS["primary_light"],
            command=self._on_threshold_change,
        )
        self._threshold_slider.pack(padx=20, pady=(4, 10), fill="x")
        self._threshold_slider.set(app.settings.get("confidence_threshold", 0.6))

        self._interval_label = ctk.CTkLabel(
            recog_card,
            text=f"Recognition Interval:  {app.settings.get('recognition_interval', 500)}ms",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            text_color=COLORS["text_secondary"],
        )
        self._interval_label.pack(padx=20, anchor="w")

        self._interval_slider = ctk.CTkSlider(
            recog_card, from_=200, to=2000, number_of_steps=36,
            fg_color=COLORS["bg_elevated"], progress_color=COLORS["primary"],
            button_color=COLORS["primary"], button_hover_color=COLORS["primary_light"],
            command=self._on_interval_change,
        )
        self._interval_slider.pack(padx=20, pady=(4, 16), fill="x")
        self._interval_slider.set(app.settings.get("recognition_interval", 500))

        # ── Right Column ──
        right = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                        scrollbar_button_color=COLORS["bg_elevated"])
        right.grid(row=1, column=1, padx=(8, 20), pady=(12, 20), sticky="nsew")
        right.grid_columnconfigure(0, weight=1)

        # Appearance Card
        appear_card = self._card(right, "Appearance")
        appear_card.pack(fill="x", pady=(0, 10))

        self._appearance_var = ctk.StringVar(value=app.settings.get("appearance_mode", "dark"))
        for mode in ["dark", "light", "system"]:
            ctk.CTkRadioButton(
                appear_card, text=mode.capitalize(), variable=self._appearance_var, value=mode,
                font=ctk.CTkFont(family=FONT_FAMILY, size=13),
                fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
                command=self._on_appearance_change,
            ).pack(padx=20, pady=3, anchor="w")

        ctk.CTkFrame(appear_card, fg_color="transparent", height=10).pack()

        # Data Management Card
        data_card = self._card(right, "Data Management")
        data_card.pack(fill="x", pady=(0, 10))

        self._retrain_btn = ctk.CTkButton(
            data_card, text="Retrain Model", height=38,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            corner_radius=10, command=self._retrain_model,
        )
        self._retrain_btn.pack(padx=16, pady=(0, 4), fill="x")

        self._retrain_status = ctk.CTkLabel(
            data_card, text="",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=COLORS["text_muted"],
        )
        self._retrain_status.pack(padx=16, pady=(0, 8))

        ctk.CTkButton(
            data_card, text="Open Faces Folder", height=36,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            fg_color=COLORS["bg_elevated"], hover_color=COLORS["bg_card_hover"],
            corner_radius=10,
            command=lambda: self._open_folder(FACE_FOLDER),
        ).pack(padx=16, pady=3, fill="x")

        ctk.CTkButton(
            data_card, text="Open Attendance Folder", height=36,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            fg_color=COLORS["bg_elevated"], hover_color=COLORS["bg_card_hover"],
            corner_radius=10,
            command=lambda: self._open_folder(ATTENDANCE_FOLDER),
        ).pack(padx=16, pady=(3, 16), fill="x")

        # Save Button
        ctk.CTkButton(
            right, text="Save All Settings", height=46,
            font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"),
            fg_color=COLORS["success"], hover_color=COLORS["success_hover"],
            corner_radius=12, command=self._save_settings,
        ).pack(fill="x", pady=(4, 0))

    def _card(self, parent, title):
        card = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=14,
                             border_width=1, border_color=COLORS["border"])
        ctk.CTkLabel(
            card, text=title,
            font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(padx=16, pady=(14, 10), anchor="w")
        return card

    def on_show(self):
        pass

    def on_hide(self):
        pass

    def _on_threshold_change(self, val):
        self._threshold_label.configure(text=f"Confidence Threshold:  {val:.0%}")

    def _on_interval_change(self, val):
        self._interval_label.configure(text=f"Recognition Interval:  {int(val)}ms")

    def _apply_camera(self):
        source = self._cam_source_var.get()
        if source == "usb":
            try:
                idx = int(self._cam_index_entry.get())
            except ValueError:
                idx = 0
            self._app.camera.switch_source(idx)
        else:
            url = self._cam_url_entry.get().strip()
            if url:
                self._app.camera.switch_source(url)
        self._cam_status.configure(text="Camera source updated", text_color=COLORS["success"])

    def _on_appearance_change(self):
        ctk.set_appearance_mode(self._appearance_var.get())

    def _retrain_model(self):
        self._retrain_btn.configure(state="disabled")
        self._retrain_status.configure(text="Training in progress...", text_color=COLORS["warning"])

        def _worker():
            result = self._app.face_engine.train_model()
            self.after(0, self._on_retrain_done, result)

        threading.Thread(target=_worker, daemon=True).start()

    def _on_retrain_done(self, result):
        self._retrain_btn.configure(state="normal")
        if result.get("success"):
            self._retrain_status.configure(
                text=f"Accuracy: {result['accuracy']:.1%}  |  {result['students']} students  |  {result['samples']} samples",
                text_color=COLORS["success"],
            )
            self._app.status_bar.update_model(True, result["students"])
        else:
            self._retrain_status.configure(
                text=f"Failed: {result.get('error', 'Unknown')}",
                text_color=COLORS["danger"],
            )

    def _open_folder(self, path):
        os.makedirs(path, exist_ok=True)
        os.startfile(path)

    def _save_settings(self):
        settings = {
            "camera_source": self._cam_source_var.get(),
            "camera_index": int(self._cam_index_entry.get() or 0),
            "camera_url": self._cam_url_entry.get().strip(),
            "confidence_threshold": round(self._threshold_slider.get(), 2),
            "recognition_interval": int(self._interval_slider.get()),
            "appearance_mode": self._appearance_var.get(),
        }
        self._app.settings = settings
        import config
        config.CONFIDENCE_THRESHOLD = settings["confidence_threshold"]
        save_settings(settings)
