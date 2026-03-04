# ============================================================
# VALIDATORS
# Cleans OCR output and validates values based on field rules
# ============================================================

import re
from utils.logging import debug, error


# ------------------------------------------------------------
# Validate value according to field type and validation rules
# ------------------------------------------------------------
def validate(value, field_type, rules):

    # reject empty values
    if value == "":
        return False, "empty"

    try:
        # type conversion
        if field_type == "float":
            value = float(value)

        elif field_type == "int":
            value = int(value)

        elif field_type == "string":
            value = value.strip()

    except:
        error("Type conversion failed")
        return False, "type_conversion_failed"

    # regex validation
    if "regex" in rules:
        if not re.match(rules["regex"], str(value)):
            debug("Regex validation failed", enabled=True)
            return False, "regex_failed"

    # numeric bounds
    if "min" in rules and value < rules["min"]:
        return False, "below_min"

    if "max" in rules and value > rules["max"]:
        return False, "above_max"

    # string length validation
    if "min_length" in rules and len(str(value)) < rules["min_length"]:
        return False, "too_short"

    return True, value


# ------------------------------------------------------------
# Clean raw OCR output before validation
# ------------------------------------------------------------
def clean_value(raw, field_type):

    raw = raw.strip()

    # extract numeric patterns for floats
    if field_type == "float":
        cleaned = re.findall(r"\d+\.\d+|\d+", raw)
        return cleaned[0] if cleaned else ""

    # extract digits for integers
    if field_type == "int":
        cleaned = re.findall(r"\d+", raw)
        return cleaned[0] if cleaned else ""

    # normalize whitespace for strings
    if field_type == "string":
        return " ".join(raw.split())

    return raw