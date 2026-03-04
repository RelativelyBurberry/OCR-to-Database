# ============================================================
# SIMPLE LOGGER
# Writes logs to console and logs/app.log
# ============================================================

import datetime
import os

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# ensure logs directory exists
os.makedirs(LOG_DIR, exist_ok=True)


# ------------------------------------------------------------
# Write raw log text to file
# ------------------------------------------------------------
def write_log(text):

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")


# ------------------------------------------------------------
# Standard log
# ------------------------------------------------------------
def log(message):

    now = datetime.datetime.now().strftime("%H:%M:%S")
    text = f"[{now}] {message}"

    print(text)
    write_log(text)


# ------------------------------------------------------------
# Debug log (only if enabled)
# ------------------------------------------------------------
def debug(message, enabled=False):

    if enabled:
        log(f"[DEBUG] {message}")


# ------------------------------------------------------------
# Error log
# ------------------------------------------------------------
def error(message):

    log(f"[ERROR] {message}")