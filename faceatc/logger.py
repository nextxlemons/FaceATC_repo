"""
App-wide logging setup. Import get_logger() anywhere you need to log.
"""
import logging
from config import LOG_PATH, ensure_dirs

_configured = False


def get_logger(name: str = "faceatc") -> logging.Logger:
    global _configured
    if not _configured:
        ensure_dirs()
        logging.basicConfig(
            filename=LOG_PATH,
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )
        # Also echo to console during development
        console = logging.StreamHandler()
        console.setLevel(logging.WARNING)
        console.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        logging.getLogger().addHandler(console)
        _configured = True
    return logging.getLogger(name)
