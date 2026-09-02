import os
import pickle
import numpy as np
import cv2
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from deepface import DeepFace

import config
from utils.image_utils import augment_image, resize_image


class _SingleClassModel:
    """Fallback model when only one student is registered.
    Uses cosine similarity against the mean embedding."""

    def __init__(self, embeddings, label):
        self._centroid = np.mean(embeddings, axis=0)
        self._label = label
        self._std = max(np.std(np.linalg.norm(embeddings - self._centroid, axis=1)), 1e-6)

    def predict(self, X):
        return np.array([self._label] * len(X))

    def predict_proba(self, X):
        distances = np.linalg.norm(X - self._centroid, axis=1)
        confidence = np.exp(-distances / (self._std * 3))
        proba = np.column_stack([confidence, 1 - confidence])
        return proba


class FaceEngine:
    def __init__(self):
        self.svm_model = None
        self.label_dict = {}
        self.reverse_label_dict = {}
        self._model_path = os.path.join(config.MODEL_FOLDER, config.SVM_MODEL_FILE)
        self._label_path = os.path.join(config.MODEL_FOLDER, config.LABEL_DICT_FILE)

    @property
    def is_loaded(self):
        return self.svm_model is not None

    @property
    def student_count(self):
        return len(self.label_dict)

    def load_model(self):
        if os.path.exists(self._model_path) and os.path.exists(self._label_path):
            with open(self._model_path, "rb") as f:
                self.svm_model = pickle.load(f)
            with open(self._label_path, "rb") as f:
                self.label_dict = pickle.load(f)
            self.reverse_label_dict = {v: k for k, v in self.label_dict.items()}
            return True
        return False

    def train_model(self, progress_callback=None):
        faces_folder = config.FACE_FOLDER
        if not os.path.exists(faces_folder):
            return {"success": False, "error": "Faces folder not found"}

        student_dirs = [d for d in os.listdir(faces_folder)
                        if os.path.isdir(os.path.join(faces_folder, d))]
        total_students = len(student_dirs)

        if total_students < 1:
            return {"success": False, "error": "No student folders found"}

        X_embeddings = []
        y_labels = []
        label_dict = {}
        current_label = 0

        for idx, student_dir in enumerate(student_dirs):
            student_path = os.path.join(faces_folder, student_dir)

            label_dict[student_dir] = current_label
            student_embeddings_count = 0

            for file_name in os.listdir(student_path):
                file_path = os.path.join(student_path, file_name)
                if not file_path.lower().endswith((".png", ".jpg", ".jpeg")):
                    continue

                img = cv2.imread(file_path)
                if img is None:
                    continue

                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img_resized = resize_image(img_rgb, config.TARGET_IMAGE_SIZE)

                embedding = self._extract_embedding(img_resized)
                if embedding is not None:
                    X_embeddings.append(embedding)
                    y_labels.append(current_label)
                    student_embeddings_count += 1

                for aug_img in augment_image(img_resized, config.AUGMENTATION_COUNT):
                    emb = self._extract_embedding(aug_img)
                    if emb is not None:
                        X_embeddings.append(emb)
                        y_labels.append(current_label)
                        student_embeddings_count += 1

            if student_embeddings_count == 0:
                del label_dict[student_dir]
            else:
                current_label += 1

            if progress_callback:
                progress_callback((idx + 1) / total_students)

        if len(X_embeddings) < 2:
            return {"success": False, "error": "Not enough face data to train"}

        X = np.array(X_embeddings)
        y = np.array(y_labels)
        unique_labels = np.unique(y)

        if len(unique_labels) == 1:
            model = _SingleClassModel(X, unique_labels[0])
            accuracy = 1.0
        else:
            model = SVC(kernel="linear", probability=True)
            min_class_count = min(np.bincount(y)[np.bincount(y) > 0])
            if min_class_count >= 2 and len(y) >= 5:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42, stratify=y
                )
                model.fit(X_train, y_train)
                predictions = model.predict(X_test)
                accuracy = accuracy_score(y_test, predictions)
            else:
                model.fit(X, y)
                accuracy = 1.0

        os.makedirs(config.MODEL_FOLDER, exist_ok=True)
        with open(self._model_path, "wb") as f:
            pickle.dump(model, f)
        with open(self._label_path, "wb") as f:
            pickle.dump(label_dict, f)

        self.svm_model = model
        self.label_dict = label_dict
        self.reverse_label_dict = {v: k for k, v in label_dict.items()}

        return {
            "success": True,
            "accuracy": accuracy,
            "students": len(label_dict),
            "samples": len(X_embeddings),
        }

    def recognize_faces(self, frame):
        if not self.is_loaded:
            return []

        results = []
        try:
            face_objs = DeepFace.extract_faces(
                frame, detector_backend="opencv", enforce_detection=False
            )
        except Exception:
            return []

        for face_obj in face_objs:
            facial_area = face_obj.get("facial_area", {})
            x = facial_area.get("x", 0)
            y = facial_area.get("y", 0)
            w = facial_area.get("w", 0)
            h = facial_area.get("h", 0)

            if w < 30 or h < 30:
                continue

            det_confidence = face_obj.get("confidence", 0)
            if det_confidence < 0.5:
                continue

            face_crop = frame[y : y + h, x : x + w]
            if face_crop.size == 0:
                continue

            embedding = self._extract_embedding(face_crop)
            if embedding is None:
                continue

            embedding = np.array(embedding).reshape(1, -1)
            prediction = self.svm_model.predict(embedding)[0]
            proba = self.svm_model.predict_proba(embedding)
            confidence = float(np.max(proba))
            name = self.reverse_label_dict.get(prediction, "Unknown")

            results.append({
                "name": name,
                "confidence": confidence,
                "bbox": (x, y, w, h),
            })

        return results

    def _extract_embedding(self, img):
        try:
            if img.dtype != np.uint8:
                img = (img * 255).astype(np.uint8) if img.max() <= 1.0 else img.astype(np.uint8)
            result = DeepFace.represent(
                img_path=img,
                model_name=config.DEEPFACE_MODEL,
                enforce_detection=False,
            )
            if result:
                return result[0]["embedding"]
        except Exception:
            pass
        return None
