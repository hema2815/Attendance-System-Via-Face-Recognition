import customtkinter as ctk
from config import COLORS, FONT_FAMILY


class StatusBar(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, height=32, corner_radius=0,
                         fg_color=COLORS["bg_card"], border_width=0)
        self._app = app
        self.grid_propagate(False)
        self.grid_columnconfigure(4, weight=1)

        dot_font = ctk.CTkFont(size=8)
        label_font = ctk.CTkFont(family=FONT_FAMILY, size=11)

        self._camera_dot = ctk.CTkLabel(self, text="●", font=ctk.CTkFont(size=11),
                                         text_color=COLORS["danger"], width=14)
        self._camera_dot.grid(row=0, column=0, padx=(14, 3), pady=4)

        self._camera_label = ctk.CTkLabel(self, text="Camera: Disconnected",
                                           font=label_font, text_color=COLORS["text_muted"])
        self._camera_label.grid(row=0, column=1, padx=(0, 20), pady=4)

        self._session_label = ctk.CTkLabel(self, text="Session: Inactive",
                                            font=label_font, text_color=COLORS["text_muted"])
        self._session_label.grid(row=0, column=2, padx=20, pady=4)

        self._model_label = ctk.CTkLabel(self, text="Model: Not Loaded",
                                          font=label_font, text_color=COLORS["text_muted"])
        self._model_label.grid(row=0, column=5, padx=(20, 14), pady=4)

    def update_camera(self, connected):
        if connected:
            self._camera_dot.configure(text_color=COLORS["success"])
            self._camera_label.configure(text="Camera: Connected", text_color=COLORS["text_secondary"])
        else:
            self._camera_dot.configure(text_color=COLORS["danger"])
            self._camera_label.configure(text="Camera: Disconnected", text_color=COLORS["text_muted"])

    def update_session(self, active, duration="00:00:00", count=0):
        if active:
            self._session_label.configure(
                text=f"Session: Active  •  {duration}  •  {count} present",
                text_color=COLORS["success"],
            )
        else:
            self._session_label.configure(text="Session: Inactive", text_color=COLORS["text_muted"])

    def update_model(self, loaded, student_count=0):
        if loaded:
            self._model_label.configure(
                text=f"Model: {student_count} student{'s' if student_count != 1 else ''}",
                text_color=COLORS["text_secondary"],
            )
        else:
            self._model_label.configure(text="Model: Not Loaded", text_color=COLORS["warning"])
