import threading
from contextlib import contextmanager


class LockVisible:
    """Un Lock normal que además recuerda quién lo tiene (para mostrarlo)."""

    def __init__(self):
        self._lock = threading.Lock()
        self.dueno = None

    @contextmanager
    def de(self, quien):
        self._lock.acquire()
        self.dueno = quien
        try:
            yield
        finally:
            self.dueno = None
            self._lock.release()
