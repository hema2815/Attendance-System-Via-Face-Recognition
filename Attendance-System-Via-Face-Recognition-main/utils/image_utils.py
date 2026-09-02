import cv2
import numpy as np
from PIL import Image
import customtkinter as ctk


def augment_image(img, count=3):
    results = []
    h, w = img.shape[:2]
    center = (w // 2, h // 2)

    for i in range(count):
        aug = img.copy()

        angle = np.random.uniform(-20, 20)
        M_rot = cv2.getRotationMatrix2D(center, angle, 1.0)
        aug = cv2.warpAffine(aug, M_rot, (w, h), borderMode=cv2.BORDER_REFLECT_101)

        tx = np.random.uniform(-0.15, 0.15) * w
        ty = np.random.uniform(-0.15, 0.15) * h
        M_shift = np.float32([[1, 0, tx], [0, 1, ty]])
        aug = cv2.warpAffine(aug, M_shift, (w, h), borderMode=cv2.BORDER_REFLECT_101)

        zoom = np.random.uniform(0.85, 1.15)
        M_zoom = cv2.getRotationMatrix2D(center, 0, zoom)
        aug = cv2.warpAffine(aug, M_zoom, (w, h), borderMode=cv2.BORDER_REFLECT_101)

        if np.random.random() > 0.5:
            aug = cv2.flip(aug, 1)

        brightness = np.random.uniform(0.8, 1.2)
        aug = np.clip(aug * brightness, 0, 255).astype(np.uint8)

        results.append(aug)

    return results


def resize_image(img, size=(160, 160)):
    return cv2.resize(img, size, interpolation=cv2.INTER_AREA)


def frame_to_pil(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)


def pil_to_ctk_image(pil_img, size=(640, 480)):
    return ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=size)


def draw_face_boxes(frame, detections):
    display = frame.copy()
    overlay = display.copy()

    for det in detections:
        x, y, w, h = det["bbox"]
        name = det["name"]
        conf = det["confidence"]

        if conf > 0.6:
            color = (99, 255, 108)
            bg_color = (30, 60, 35)
        else:
            color = (100, 180, 255)
            bg_color = (35, 45, 60)

        corner_len = min(w, h) // 4
        thickness = 2

        cv2.line(display, (x, y), (x + corner_len, y), color, thickness)
        cv2.line(display, (x, y), (x, y + corner_len), color, thickness)
        cv2.line(display, (x + w, y), (x + w - corner_len, y), color, thickness)
        cv2.line(display, (x + w, y), (x + w, y + corner_len), color, thickness)
        cv2.line(display, (x, y + h), (x + corner_len, y + h), color, thickness)
        cv2.line(display, (x, y + h), (x, y + h - corner_len), color, thickness)
        cv2.line(display, (x + w, y + h), (x + w - corner_len, y + h), color, thickness)
        cv2.line(display, (x + w, y + h), (x + w, y + h - corner_len), color, thickness)

        label = f"{name}  {conf:.0%}"
        font_scale = 0.55
        font_thickness = 1
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)[0]
        lw, lh = label_size[0] + 16, label_size[1] + 14
        lx, ly = x, y - lh - 4
        if ly < 0:
            ly = y + h + 4

        cv2.rectangle(overlay, (lx, ly), (lx + lw, ly + lh), bg_color, -1)
        cv2.addWeighted(overlay, 0.85, display, 0.15, 0, display)
        cv2.putText(display, label, (lx + 8, ly + lh - 7),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, font_thickness, cv2.LINE_AA)

    return display
