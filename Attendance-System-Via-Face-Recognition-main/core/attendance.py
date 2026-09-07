import uuid
from datetime import datetime

from utils.excel_export import export_session_to_excel
import config


class AttendanceSession:
    def __init__(self):
        self.session_id = str(uuid.uuid4())[:8]
        self.start_time = None
        self.end_time = None
        self.is_active = False
        self.marked_students = set()
        self.records = []

    @staticmethod
    def _extract_student_id(name):
        value = str(name).strip()
        if "_" in value:
            return value.rsplit("_", 1)[-1]
        return value

    @staticmethod
    def _display_name(name):
        value = str(name).strip()
        if "_" in value:
            value = value.rsplit("_", 1)[0]
        return value.replace("_", " ")

    def start(self):
        self.session_id = str(uuid.uuid4())[:8]
        self.start_time = datetime.now()
        self.end_time = None
        self.is_active = True
        self.marked_students.clear()
        self.records.clear()

    def stop(self):
        self.end_time = datetime.now()
        self.is_active = False
        if self.records:
            return export_session_to_excel(
                self.records, self.start_time, config.ATTENDANCE_FOLDER
            )
        return None

    def mark_attendance(self, name, confidence):
        if not self.is_active:
            return False

        if not name or str(name).strip().lower() == "unknown":
            return False
        if confidence < config.CONFIDENCE_THRESHOLD:
            return False

        student_id = self._extract_student_id(name)
        display_name = self._display_name(name)
        attendance_key = student_id.lower()

        # Use the student ID as the unique key. This prevents two students
        # with the same name from being treated as the same person.
        if attendance_key in self.marked_students:
            return False

        self.marked_students.add(attendance_key)
        now = datetime.now()
        self.records.append({
            "student_id": student_id,
            "name": display_name,
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "confidence": round(float(confidence), 4),
        })
        return True

    def get_records(self):
        return list(self.records)

    @property
    def count(self):
        return len(self.marked_students)

    @property
    def duration(self):
        if self.start_time is None:
            return "00:00:00"
        end = self.end_time or datetime.now()
        delta = end - self.start_time
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
