import os
import re
import cv2
import shutil

import config
from utils.image_utils import augment_image


class StudentManager:
    def __init__(self, face_engine):
        self._face_engine = face_engine

    @staticmethod
    def _normalise_id(student_id):
        return str(student_id).strip().lower()

    @staticmethod
    def _safe_folder_name(name, student_id):
        clean_name = re.sub(r"[^A-Za-z0-9_-]+", "_", str(name).strip())
        clean_id = re.sub(r"[^A-Za-z0-9_-]+", "_", str(student_id).strip())
        return f"{clean_name}_{clean_id}".strip("_")

    def _student_id_exists(self, student_id, exclude_folder=None):
        target_id = self._normalise_id(student_id)
        if not os.path.exists(config.FACE_FOLDER):
            return False

        for folder_name in os.listdir(config.FACE_FOLDER):
            if folder_name == exclude_folder:
                continue
            full_path = os.path.join(config.FACE_FOLDER, folder_name)
            if not os.path.isdir(full_path) or "_" not in folder_name:
                continue
            existing_id = folder_name.rsplit("_", 1)[-1]
            if self._normalise_id(existing_id) == target_id:
                return True
        return False

    def list_students(self):
        students = []
        if not os.path.exists(config.FACE_FOLDER):
            return students

        for folder_name in sorted(os.listdir(config.FACE_FOLDER)):
            full = os.path.join(config.FACE_FOLDER, folder_name)
            if not os.path.isdir(full):
                continue

            images = [
                f for f in os.listdir(full)
                if f.lower().endswith((".png", ".jpg", ".jpeg"))
            ]
            if "_" in folder_name:
                name, student_id = folder_name.rsplit("_", 1)
            else:
                name, student_id = folder_name, ""

            students.append({
                "folder": folder_name,
                "name": name.replace("_", " "),
                "student_id": student_id,
                "image_count": len(images),
            })
        return students

    def register_student(self, name, student_id, images, progress_callback=None):
        name = str(name).strip()
        student_id = str(student_id).strip()

        if not name:
            return {"success": False, "error": "Student name is required"}
        if not student_id:
            return {"success": False, "error": "Student ID is required"}
        if not images:
            return {"success": False, "error": "At least one face image is required"}
        if self._student_id_exists(student_id):
            return {"success": False, "error": f"Student ID {student_id} is already registered"}

        folder_name = self._safe_folder_name(name, student_id)
        folder_path = os.path.join(config.FACE_FOLDER, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        try:
            for i, img in enumerate(images):
                path = os.path.join(folder_path, f"img_{i + 1:03d}.jpg")
                if not cv2.imwrite(path, img):
                    raise IOError(f"Could not save image {i + 1}")

                aug_images = augment_image(
                    cv2.cvtColor(img, cv2.COLOR_BGR2RGB) if len(img.shape) == 3 else img,
                    config.AUGMENTATION_COUNT,
                )
                for j, aug in enumerate(aug_images):
                    aug_bgr = cv2.cvtColor(aug, cv2.COLOR_RGB2BGR)
                    aug_path = os.path.join(
                        folder_path, f"img_{i + 1:03d}_aug_{j + 1}.jpg"
                    )
                    cv2.imwrite(aug_path, aug_bgr)

            if progress_callback:
                progress_callback(0.5)

            result = self._face_engine.train_model(progress_callback=progress_callback)
            if not result.get("success"):
                shutil.rmtree(folder_path, ignore_errors=True)
                self._face_engine.load_model()
                return result
            return result
        except Exception as exc:
            shutil.rmtree(folder_path, ignore_errors=True)
            self._face_engine.load_model()
            return {"success": False, "error": str(exc)}

    def delete_student(self, folder_name):
        folder_path = os.path.join(config.FACE_FOLDER, folder_name)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            self._face_engine.train_model()
            return True
        return False
