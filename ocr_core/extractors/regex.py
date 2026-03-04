# ============================================================
# REGEX EXTRACTION
# Extracts text from OCR output using a regex pattern
# ============================================================

import re
from utils.logging import debug, error


def extract_regex(text, field_config):

    pattern = field_config["pattern"]

    debug(f"Running regex extraction with pattern: {pattern}", enabled=True)

    try:
        match = re.search(pattern, text)

        if match:
            result = match.group()
            debug(f"Regex match found: {result}", enabled=True)
            return result

    except Exception as e:
        error(f"Regex extraction failed: {e}")

    return ""