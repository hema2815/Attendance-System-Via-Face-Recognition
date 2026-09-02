import threading
from collections import defaultdict


class EventBus:
    def __init__(self, root=None):
        self._root = root
        self._subscribers = defaultdict(list)
        self._lock = threading.Lock()

    def set_root(self, root):
        self._root = root

    def subscribe(self, event_name, callback):
        with self._lock:
            self._subscribers[event_name].append(callback)

    def unsubscribe(self, event_name, callback):
        with self._lock:
            if callback in self._subscribers[event_name]:
                self._subscribers[event_name].remove(callback)

    def publish(self, event_name, data=None):
        with self._lock:
            callbacks = list(self._subscribers[event_name])
        for cb in callbacks:
            if self._root:
                self._root.after(0, cb, data)
            else:
                cb(data)
