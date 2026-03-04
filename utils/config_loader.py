# ============================================================
# TEMPLATE CONFIG LOADER
# Loads OCR templates stored as JSON files
# ============================================================

import json
import os

from utils.logging import log, debug, error


TEMPLATE_DIR = os.path.join("configs", "templates")


# ------------------------------------------------------------
# Load a specific template
# ------------------------------------------------------------
def load_template(template_name):
    """
    Loads a template JSON from configs/templates/
    """

    path = os.path.join(TEMPLATE_DIR, f"{template_name}.json")

    if not os.path.exists(path):
        error(f"Template not found: {path}")
        raise FileNotFoundError(f"Template not found: {path}")

    log(f"Loading template: {template_name}")

    with open(path, "r") as f:
        return json.load(f)


# ------------------------------------------------------------
# List available templates
# ------------------------------------------------------------
def list_templates():
    """
    Returns all available template names
    """

    if not os.path.exists(TEMPLATE_DIR):
        debug("Template directory does not exist yet", enabled=True)
        return []

    files = [
        f.replace(".json", "")
        for f in os.listdir(TEMPLATE_DIR)
        if f.endswith(".json")
    ]

    debug(f"Templates found: {files}", enabled=True)

    return files