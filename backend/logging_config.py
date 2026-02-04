import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import date
import os

SERVICE_NAME = os.getenv("SERVICE_NAME", "backend")

# ✅ REPO ROOT (backend is ONE level below repo)
REPO_ROOT = Path(__file__).resolve().parents[1]

TODAY = date.today().isoformat()
LOG_DIR = REPO_ROOT / "logs" / SERVICE_NAME / TODAY
LOG_DIR.mkdir(parents=True, exist_ok=True)

APP_LOG = LOG_DIR / "app.log"
DEBUG_LOG = LOG_DIR / "debug.log"
ERROR_LOG = LOG_DIR / "error.log"


def setup_logging():
    print("🔥 BACKEND LOG_DIR =", LOG_DIR)  # TEMP: verify

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | "
        f"{SERVICE_NAME} | %(message)s"
    )

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.handlers.clear()

    def handler(path, level):
        h = RotatingFileHandler(
            path,
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        h.setLevel(level)
        h.setFormatter(formatter)
        return h

    root.addHandler(handler(APP_LOG, logging.INFO))
    root.addHandler(handler(DEBUG_LOG, logging.DEBUG))
    root.addHandler(handler(ERROR_LOG, logging.ERROR))
