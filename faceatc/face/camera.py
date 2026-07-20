"""
Safe camera open/read/release lifecycle.
Use as a context manager so the camera always releases, even on error.
"""
import cv2
from logger import get_logger

log = get_logger(__name__)


class Camera:
    def __init__(self, source):
        self.source = source
        self.cap = None

    def open(self):
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open camera source: {self.source}")
        log.info(f"Camera opened: {self.source}")
        return self.cap

    def read(self):
        if self.cap is None or not self.cap.isOpened():
            return False, None
        return self.cap.read()

    def is_opened(self) -> bool:
        return self.cap is not None and self.cap.isOpened()

    def release(self):
        if self.cap is not None:
            self.cap.release()
            log.info(f"Camera released: {self.source}")
            self.cap = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        # Don't suppress exceptions
        return False
