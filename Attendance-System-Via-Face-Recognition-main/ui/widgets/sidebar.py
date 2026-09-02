import customtkinter as ctk
from config import COLORS, FONT_FAMILY


class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, width=240, corner_radius=0, fg_color=COLORS["bg_sidebar"],
                         border_width=0)
        self._app = app
        self._buttons = {}
        self._indicators = {}
        self._active = None

        self.grid_rowconfigure(10, weight=1)
        self.grid_propagate(False)

        brand_frame = ctk.CTkFrame(self, fg_color="transparent")
        brand_frame.grid(row=0, column=0, padx=24, pady=(30, 0), sticky="ew")

        logo_bar = ctk.CTkFrame(brand_frame, fg_color=COLORS["primary"], corner_radius=8,
                                width=40, height=40)
        logo_bar.pack(anchor="w")
        logo_bar.pack_propagate(False)
        ctk.CTkLabel(logo_bar, text="FA", font=ctk.CTkFont(family=FONT_FAMILY, size=16, weight="bold"),
                     text_color="#FFFFFF").place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            brand_frame, text="FaceAttend",
            font=ctk.CTkFont(family=FONT_FAMILY, size=22, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", pady=(8, 0))

        ctk.CTkLabel(
            brand_frame, text="Smart Attendance System",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(2, 0))

        sep = ctk.CTkFrame(self, height=1, fg_color=COLORS["border"])
        sep.grid(row=1, column=0, padx=20, pady=(20, 16), sticky="ew")

        ctk.CTkLabel(
            self, text="NAVIGATION",
            font=ctk.CTkFont(family=FONT_FAMILY, size=10, weight="bold"),
            text_color=COLORS["text_muted"],
        ).grid(row=2, column=0, padx=28, pady=(0, 8), sticky="w")

        nav_items = [
            ("dashboard", "Dashboard", 3),
            ("register", "Register Student", 4),
            ("attendance", "Attendance Log", 5),
            ("settings", "Settings", 6),
        ]

        for screen_name, label, row in nav_items:
            container = ctk.CTkFrame(self, fg_color="transparent", height=42)
            container.grid(row=row, column=0, padx=12, pady=2, sticky="ew")
            container.grid_propagate(False)
            container.grid_columnconfigure(1, weight=1)

            indicator = ctk.CTkFrame(container, width=3, height=24, corner_radius=2,
                                     fg_color="transparent")
            indicator.grid(row=0, column=0, padx=(0, 0), pady=9)
            self._indicators[screen_name] = indicator

            btn = ctk.CTkButton(
                container, text=f"  {label}",
                font=ctk.CTkFont(family=FONT_FAMILY, size=14),
                height=42, anchor="w",
                fg_color="transparent",
                text_color=COLORS["text_secondary"],
                hover_color=COLORS["bg_elevated"],
                corner_radius=10,
                command=lambda s=screen_name: self._navigate(s),
            )
            btn.grid(row=0, column=1, sticky="ew", padx=(4, 8))
            self._buttons[screen_name] = btn

        sep2 = ctk.CTkFrame(self, height=1, fg_color=COLORS["border"])
        sep2.grid(row=11, column=0, padx=20, pady=(10, 10), sticky="sew")

        footer = ctk.CTkLabel(
            self, text="v1.0.0",
            font=ctk.CTkFont(family=FONT_FAMILY, size=10),
            text_color=COLORS["text_muted"],
        )
        footer.grid(row=12, column=0, padx=24, pady=(0, 16), sticky="sw")

        self.set_active("dashboard")

    def _navigate(self, screen_name):
        self.set_active(screen_name)
        self._app.show_screen(screen_name)

    def set_active(self, screen_name):
        self._active = screen_name
        for name, btn in self._buttons.items():
            ind = self._indicators[name]
            if name == screen_name:
                btn.configure(fg_color=COLORS["bg_elevated"], text_color=COLORS["primary_light"])
                ind.configure(fg_color=COLORS["primary"])
            else:
                btn.configure(fg_color="transparent", text_color=COLORS["text_secondary"])
                ind.configure(fg_color="transparent")
