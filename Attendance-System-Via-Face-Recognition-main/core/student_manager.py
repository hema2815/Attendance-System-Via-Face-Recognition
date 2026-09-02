import os
import cv2
import shutil

import config
from utils.image_utils import augment_image


class StudentManager:
    def __init__(self, face_engine):
        self._face_engine = face_engine

    def list_students(self):
        students = []
        if not os.path.exists(config.FACE_FOLDER):
            return students
        for d in sorted(os.listdir(config.FACE_FOLDER)):
            full = os.path.join(config.FACE_FOLDER, d)
            if os.path.isdir(full):
                images = [f for f in os.listdir(full)
                          if f.lower().endswith((".png", ".jpg", ".jpeg"))]
                students.append({"folder": d, "image_count": len(images)})
        return students

    def register_student(self, name, student_id, images, progress_callback=None):
        folder_name = f"{name}_{student_id}".replace(" ", "_")
        folder_path = os.path.join(config.FACE_FOLDER, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        for i, img in enumerate(images):
            path = os.path.join(folder_path, f"img_{i + 1:03d}.jpg")
            cv2.imwrite(path, img)

            aug_images = augment_image(
                cv2.cvtColor(img, cv2.COLOR_BGR2RGB) if len(img.shape) == 3 else img,
                config.AUGMENTATION_COUNT,
            )
            for j, aug in enumerate(aug_images):
                aug_bgr = cv2.cvtColor(aug, cv2.COLOR_RGB2BGR)
                aug_path = os.path.join(folder_path, f"img_{i + 1:03d}_aug_{j + 1}.jpg")
                cv2.imwrite(aug_path, aug_bgr)

        if progress_callback:
            progress_callback(0.5)

        result = self._face_engine.train_model(progress_callback=progress_callback)
        return result

    def delete_student(self, folder_name):
        folder_path = os.path.join(config.FACE_FOLDER, folder_name)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            self._face_engine.train_model()
            return True
        return False
