import threading
import time
import cv2
import numpy as np


class CameraThread(threading.Thread):
    def __init__(self, source=0, event_bus=None):
        super().__init__(daemon=True)
        self._source = source
        self._event_bus = event_bus
        self._frame = None
        self._lock = threading.Lock()
        self._running = threading.Event()
        self._running.set()
        self._connected = False
        self._cap = None

    @property
    def is_connected(self):
        return self._connected

    def get_frame(self):
        with self._lock:
            return self._frame.copy() if self._frame is not None else None

    def switch_source(self, source):
        self._release()
        self._source = source
        self._connected = False

    def stop(self):
        self._running.clear()
        self._release()

    def _release(self):
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    def _open(self):
        self._release()
        if isinstance(self._source, str) and self._source.strip():
            self._cap = cv2.VideoCapture(self._source)
        else:
            self._cap = cv2.VideoCapture(int(self._source))
        if self._cap.isOpened():
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self._connected = True
            if self._event_bus:
                self._event_bus.publish("camera_connected")
            return True
        self._connected = False
        return False

    def run(self):
        fail_count = 0
        backoff = 1.0

        while self._running.is_set():
            if not self._connected:
                if self._open():
                    fail_count = 0
                    backoff = 1.0
                else:
                    if self._event_bus:
                        self._event_bus.publish("camera_disconnected")
                    time.sleep(min(backoff, 30.0))
                    backoff *= 2
                    continue

            ret, frame = self._cap.read()
            if ret:
                with self._lock:
                    self._frame = frame
                fail_count = 0
            else:
                fail_count += 1
                if fail_count >= 5:
                    self._connected = False
                    if self._event_bus:
                        self._event_bus.publish("camera_disconnected")
                    time.sleep(1.0)

            time.sleep(0.01)
