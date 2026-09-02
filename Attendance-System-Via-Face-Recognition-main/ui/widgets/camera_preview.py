import customtkinter as ctk
import cv2
from PIL import Image, ImageDraw, ImageFont
from config import COLORS, FONT_FAMILY
from utils.image_utils import frame_to_pil, pil_to_ctk_image


class CameraPreview(ctk.CTkFrame):
    def __init__(self, parent, camera_thread, size=(640, 480), overlay_fn=None):
        super().__init__(parent, fg_color=COLORS["bg_card"], corner_radius=12)
        self._size = size
        self._camera = camera_thread
        self._overlay_fn = overlay_fn
        self._running = False
        self._placeholder = self._make_placeholder()

        self._label = ctk.CTkLabel(self, text="", image=self._placeholder,
                                    fg_color="transparent")
        self._label.pack(padx=6, pady=6)

    def _make_placeholder(self):
        img = Image.new("RGB", self._size, color=(13, 17, 23))
        draw = ImageDraw.Draw(img)
        cx, cy = self._size[0] // 2, self._size[1] // 2

        for r in range(50, 30, -1):
            alpha = int(80 * (1 - (r - 30) / 20))
            draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                         outline=(108, 99, 255, alpha), width=1)

        draw.ellipse([cx - 30, cy - 30, cx + 30, cy + 30],
                     outline=(108, 99, 255), width=2)
        draw.line([cx - 12, cy, cx + 12, cy], fill=(108, 99, 255), width=2)
        draw.line([cx, cy - 12, cx, cy + 12], fill=(108, 99, 255), width=2)

        try:
            font = ImageFont.truetype("segoeui.ttf", 16)
        except (OSError, IOError):
            font = ImageFont.load_default()

        text = "Waiting for camera..."
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        draw.text((cx - tw // 2, cy + 50), text, fill=(139, 148, 158), font=font)

        return pil_to_ctk_image(img, self._size)

    def start(self):
        self._running = True
        self._update()

    def stop(self):
        self._running = False

    def set_overlay(self, overlay_fn):
        self._overlay_fn = overlay_fn

    def get_snapshot(self):
        return self._camera.get_frame()

    def _update(self):
        if not self._running:
            return

        frame = self._camera.get_frame()
        if frame is not None:
            if self._overlay_fn:
                frame = self._overlay_fn(frame)
            pil_img = frame_to_pil(frame)
            ctk_img = pil_to_ctk_image(pil_img, self._size)
            self._label.configure(image=ctk_img)
            self._ctk_img = ctk_img
        else:
            self._label.configure(image=self._placeholder)

        self._label.after(33, self._update)
