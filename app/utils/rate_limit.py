import threading
import time
from contextlib import contextmanager


class RateLimiter:
    def __init__(self, min_interval_seconds: float):
        self.min_interval_seconds = min_interval_seconds
        self._lock = threading.Lock()
        self._last_time = 0.0

    @contextmanager
    def wait(self):
        with self._lock:
            now = time.time()
            elapsed = now - self._last_time
            if elapsed < self.min_interval_seconds:
                time.sleep(self.min_interval_seconds - elapsed)
            self._last_time = time.time()
        yield
