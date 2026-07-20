"""
FaceATC — Face Recognition Attendance System
Entry point. Run this file to start the application:

    python main.py
"""
from config import ensure_dirs
from database.db import initialize_db
from logger import get_logger
from ui.app import App
from ui import login_screen

log = get_logger(__name__)


def main():
    ensure_dirs()
    initialize_db()
    log.info("Application starting")

    app = App()
    app.show(login_screen)
    app.run()


if __name__ == "__main__":
    main()
