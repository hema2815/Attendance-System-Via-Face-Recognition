import threading
import customtkinter as ctk
from config import COLORS, FONT_FAMILY, CAPTURE_COUNT
from ui.widgets.camera_preview import CameraPreview
from utils.image_utils import frame_to_pil, pil_to_ctk_image
from deepface import DeepFace


class RegistrationScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self._app = app
        self._captured_images = []

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)

        # ── Header ──
        ctk.CTkLabel(
            self, text="Register Student",
            font=ctk.CTkFont(family=FONT_FAMILY, size=24, weight="bold"),
            text_color=COLORS["text_primary"],
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=(16, 0), sticky="w")

        # ── Left: Camera ──
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=1, column=0, padx=(20, 8), pady=(12, 20), sticky="nsew")
        left.grid_rowconfigure(0, weight=1)
        left.grid_columnconfigure(0, weight=1)

        self._preview = CameraPreview(left, app.camera, size=(580, 420))
        self._preview.grid(row=0, column=0, sticky="nsew")

        self._capture_feedback = ctk.CTkLabel(
            left, text="",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=COLORS["text_muted"], height=24,
        )
        self._capture_feedback.grid(row=1, column=0, pady=(6, 0))

        # ── Right: Form ──
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(row=1, column=1, padx=(8, 20), pady=(12, 20), sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(5, weight=1)

        # Form Card
        form = ctk.CTkFrame(right, fg_color=COLORS["bg_card"], corner_radius=14,
                             border_width=1, border_color=COLORS["border"])
        form.grid(row=0, column=0, sticky="ew")
        form.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            form, text="Student Information",
            font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"),
            text_color=COLORS["text_primary"],
        ).grid(row=0, column=0, padx=16, pady=(16, 2), sticky="w")

        ctk.CTkLabel(
            form, text="FULL NAME",
            font=ctk.CTkFont(family=FONT_FAMILY, size=10, weight="bold"),
            text_color=COLORS["text_muted"],
        ).grid(row=1, column=0, padx=16, pady=(12, 0), sticky="w")

        self._name_entry = ctk.CTkEntry(
            form, height=40, placeholder_text="e.g. John Doe",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            fg_color=COLORS["bg_input"], border_color=COLORS["border"],
            corner_radius=10,
        )
        self._name_entry.grid(row=2, column=0, padx=16, pady=(4, 0), sticky="ew")

        ctk.CTkLabel(
            form, text="STUDENT ID",
            font=ctk.CTkFont(family=FONT_FAMILY, size=10, weight="bold"),
            text_color=COLORS["text_muted"],
        ).grid(row=3, column=0, padx=16, pady=(12, 0), sticky="w")

        self._id_entry = ctk.CTkEntry(
            form, height=40, placeholder_text="e.g. 2024001",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            fg_color=COLORS["bg_input"], border_color=COLORS["border"],
            corner_radius=10,
        )
        self._id_entry.grid(row=4, column=0, padx=16, pady=(4, 16), sticky="ew")

        # Capture Section
        capture_card = ctk.CTkFrame(right, fg_color=COLORS["bg_card"], corner_radius=14,
                                     border_width=1, border_color=COLORS["border"])
        capture_card.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        capture_card.grid_columnconfigure(0, weight=1)

        cap_header = ctk.CTkFrame(capture_card, fg_color="transparent")
        cap_header.grid(row=0, column=0, padx=16, pady=(14, 4), sticky="ew")
        cap_header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            cap_header, text="Face Capture",
            font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"),
            text_color=COLORS["text_primary"],
        ).grid(row=0, column=0, sticky="w")

        self._capture_counter = ctk.CTkLabel(
            cap_header, text=f"0 / {CAPTURE_COUNT}",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=COLORS["primary"],
        )
        self._capture_counter.grid(row=0, column=1, sticky="e")

        self._progress = ctk.CTkProgressBar(
            capture_card, height=4, corner_radius=2,
            fg_color=COLORS["bg_elevated"], progress_color=COLORS["primary"],
        )
        self._progress.grid(row=1, column=0, padx=16, pady=(4, 8), sticky="ew")
        self._progress.set(0)

        self._thumb_frame = ctk.CTkFrame(capture_card, fg_color=COLORS["bg_elevated"],
                                          corner_radius=10, height=70)
        self._thumb_frame.grid(row=2, column=0, padx=16, pady=(0, 4), sticky="ew")
        self._thumb_frame.grid_propagate(False)

        self._thumb_placeholder = ctk.CTkLabel(
            self._thumb_frame, text="Captured photos will appear here",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=COLORS["text_muted"],
        )
        self._thumb_placeholder.place(relx=0.5, rely=0.5, anchor="center")

        self._capture_btn = ctk.CTkButton(
            capture_card, text=f"Capture Photo",
            height=40, font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            corner_radius=10, command=self._capture_photo,
        )
        self._capture_btn.grid(row=3, column=0, padx=16, pady=(8, 14), sticky="ew")

        # Action Buttons
        action_frame = ctk.CTkFrame(right, fg_color="transparent")
        action_frame.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        action_frame.grid_columnconfigure((0, 1), weight=1)

        self._register_btn = ctk.CTkButton(
            action_frame, text="Register & Train Model", height=44,
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
            fg_color=COLORS["success"], hover_color=COLORS["success_hover"],
            corner_radius=10, state="disabled", command=self._register_student,
        )
        self._register_btn.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        self._reset_btn = ctk.CTkButton(
            action_frame, text="Reset", height=44,
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
            fg_color=COLORS["bg_elevated"], hover_color=COLORS["danger_hover"],
            text_color=COLORS["text_secondary"],
            corner_radius=10, command=self._reset_form,
        )
        self._reset_btn.grid(row=0, column=1, padx=(4, 0), sticky="ew")

        # Status
        self._status_label = ctk.CTkLabel(
            right, text="", font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=COLORS["text_secondary"], wraplength=320,
        )
        self._status_label.grid(row=3, column=0, pady=(8, 0))

        # Registered Students Card
        students_card = ctk.CTkFrame(right, fg_color=COLORS["bg_card"], corner_radius=14,
                                      border_width=1, border_color=COLORS["border"])
        students_card.grid(row=5, column=0, sticky="nsew", pady=(10, 0))
        students_card.grid_columnconfigure(0, weight=1)
        students_card.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            students_card, text="Registered Students",
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
            text_color=COLORS["text_primary"],
        ).grid(row=0, column=0, padx=14, pady=(12, 4), sticky="w")

        self._students_list = ctk.CTkScrollableFrame(
            students_card, fg_color="transparent",
            scrollbar_button_color=COLORS["bg_elevated"],
        )
        self._students_list.grid(row=1, column=0, sticky="nsew", padx=4, pady=(0, 8))
        self._students_list.grid_columnconfigure(0, weight=1)

    def on_show(self):
        self._preview.start()
        self._refresh_students_list()

    def on_hide(self):
        self._preview.stop()

    def _capture_photo(self):
        if len(self._captured_images) >= CAPTURE_COUNT:
            return

        frame = self._app.camera.get_frame()
        if frame is None:
            self._capture_feedback.configure(text="No camera frame available", text_color=COLORS["danger"])
            return

        try:
            faces = DeepFace.extract_faces(frame, enforce_detection=False, detector_backend="opencv")
            valid = [f for f in faces if f.get("confidence", 0) > 0.5]
            if len(valid) == 0:
                self._capture_feedback.configure(text="No face detected - try again", text_color=COLORS["danger"])
                return
            if len(valid) > 1:
                self._capture_feedback.configure(text="Multiple faces detected - only one person please", text_color=COLORS["warning"])
                return
        except Exception:
            pass

        self._captured_images.append(frame)
        count = len(self._captured_images)
        self._progress.set(count / CAPTURE_COUNT)
        self._capture_counter.configure(text=f"{count} / {CAPTURE_COUNT}")
        self._capture_feedback.configure(text=f"Photo {count} captured!", text_color=COLORS["success"])

        if self._thumb_placeholder and self._thumb_placeholder.winfo_exists():
            self._thumb_placeholder.destroy()
            self._thumb_placeholder = None

        thumb_pil = frame_to_pil(frame).resize((70, 52))
        thumb_img = pil_to_ctk_image(thumb_pil, (70, 52))
        lbl = ctk.CTkLabel(self._thumb_frame, text="", image=thumb_img,
                           fg_color="transparent", corner_radius=6)
        lbl._img = thumb_img
        lbl.pack(side="left", padx=4, pady=8)

        if count >= CAPTURE_COUNT:
            self._capture_btn.configure(state="disabled", fg_color=COLORS["bg_elevated"])
            self._register_btn.configure(state="normal")
            self._capture_feedback.configure(text="All photos captured! Click Register & Train.", text_color=COLORS["success"])

    def _register_student(self):
        name = self._name_entry.get().strip()
        student_id = self._id_entry.get().strip()

        if not name:
            self._status_label.configure(text="Please enter student name.", text_color=COLORS["danger"])
            return
        if not student_id:
            self._status_label.configure(text="Please enter student ID.", text_color=COLORS["danger"])
            return

        self._register_btn.configure(state="disabled")
        self._status_label.configure(text="Training model... This may take a minute.", text_color=COLORS["warning"])
        self._progress.set(0)

        def _worker():
            def _progress(val):
                try:
                    if self.winfo_exists():
                        self.after(0, lambda: self._safe_set_progress(val))
                except Exception:
                    pass
            result = self._app.student_manager.register_student(
                name, student_id, self._captured_images, progress_callback=_progress,
            )
            try:
                if self.winfo_exists():
                    self.after(0, self._on_training_complete, result)
            except Exception:
                pass

        threading.Thread(target=_worker, daemon=True).start()

    def _safe_set_progress(self, val):
        try:
            if self._progress.winfo_exists():
                self._progress.set(min(val, 1.0))
        except Exception:
            pass

    def _on_training_complete(self, result):
        if result.get("success"):
            acc = result.get("accuracy", 0)
            count = result.get("students", 0)
            self._status_label.configure(
                text=f"Registered successfully! Model accuracy: {acc:.1%} ({count} students)",
                text_color=COLORS["success"],
            )
            self._app.status_bar.update_model(True, self._app.face_engine.student_count)
            self._reset_form()
            self._refresh_students_list()
        else:
            self._status_label.configure(
                text=f"Training failed: {result.get('error', 'Unknown error')}",
                text_color=COLORS["danger"],
            )
            self._register_btn.configure(state="normal")

    def _reset_form(self):
        self._captured_images.clear()
        self._name_entry.delete(0, "end")
        self._id_entry.delete(0, "end")
        self._progress.set(0)
        self._capture_counter.configure(text=f"0 / {CAPTURE_COUNT}")
        self._capture_btn.configure(state="normal", fg_color=COLORS["primary"])
        self._register_btn.configure(state="disabled")
        self._capture_feedback.configure(text="")

        for w in self._thumb_frame.winfo_children():
            w.destroy()
        self._thumb_placeholder = ctk.CTkLabel(
            self._thumb_frame, text="Captured photos will appear here",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=COLORS["text_muted"],
        )
        self._thumb_placeholder.place(relx=0.5, rely=0.5, anchor="center")

    def _refresh_students_list(self):
        for w in self._students_list.winfo_children():
            w.destroy()

        students = self._app.student_manager.list_students()
        if not students:
            ctk.CTkLabel(
                self._students_list, text="No students registered yet",
                font=ctk.CTkFont(family=FONT_FAMILY, size=12),
                text_color=COLORS["text_muted"],
            ).grid(row=0, column=0, pady=16)
            return

        for i, s in enumerate(students):
            row = ctk.CTkFrame(self._students_list, fg_color=COLORS["bg_elevated"],
                                corner_radius=8, height=38)
            row.grid(row=i, column=0, sticky="ew", pady=2, padx=4)
            row.grid_columnconfigure(1, weight=1)
            row.grid_propagate(False)

            ctk.CTkLabel(
                row, text=s["folder"].replace("_", " "),
                font=ctk.CTkFont(family=FONT_FAMILY, size=12),
                text_color=COLORS["text_primary"], anchor="w",
            ).grid(row=0, column=1, padx=12, pady=8, sticky="w")

            ctk.CTkLabel(
                row, text=f"{s['image_count']} photos",
                font=ctk.CTkFont(family=FONT_FAMILY, size=10),
                text_color=COLORS["text_muted"],
            ).grid(row=0, column=2, padx=10, pady=8)
