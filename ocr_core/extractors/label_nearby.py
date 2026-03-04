# ============================================================
# LABEL NEARBY EXTRACTION
# Extracts value appearing next to a label in OCR text
# Example:
#   "Register No: 24BDS1024"  → returns "24BDS1024"
# ============================================================

from utils.logging import debug


def extract_label_nearby(text, field_config):

    label = field_config["label"]

    # scan each OCR line looking for the label
    for line in text.split("\n"):

        if label.lower() in line.lower():

            debug(f"Label match found in line: {line}", enabled=True)

            parts = line.split(label)

            if len(parts) > 1:
                return parts[1].strip()

    return ""