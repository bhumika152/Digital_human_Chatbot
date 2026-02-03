import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import date

# --------------------------------------------------
# PATH SETUP (PROJECT ROOT)
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[4]

TODAY = date.today().isoformat()  # YYYY-MM-DD
LOG_DIR = BASE_DIR / "logs" / TODAY
LOG_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# LOG FILES
# --------------------------------------------------
APP_LOG = LOG_DIR / "app.log"
INFO_LOG = LOG_DIR / "info.log"
DEBUG_LOG = LOG_DIR / "debug.log"
ERROR_LOG = LOG_DIR / "error.log"


def setup_logging():
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # ---------------------------
    # Root Logger
    # ---------------------------
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    # 🔥 CRITICAL: reset existing handlers (uvicorn, reload, etc.)
    root.handlers.clear()

    # ---------------------------
    # File Handlers
    # ---------------------------
    app_handler = RotatingFileHandler(
        APP_LOG, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(formatter)

    info_handler = RotatingFileHandler(
        INFO_LOG, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)

    debug_handler = RotatingFileHandler(
        DEBUG_LOG, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(formatter)

    error_handler = RotatingFileHandler(
        ERROR_LOG, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # ---------------------------
    # Attach handlers
    # ---------------------------
    root.addHandler(app_handler)
    root.addHandler(info_handler)
    root.addHandler(debug_handler)
    root.addHandler(error_handler)
