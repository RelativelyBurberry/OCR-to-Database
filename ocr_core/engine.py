# ============================================================
# OCR ENGINE
# Runs OCR on an image using a selected template
# ============================================================

from PIL import Image
import pytesseract

from ocr_core.extractors.registry import EXTRACTORS
from ocr_core.validators import validate, clean_value

from utils.logging import log, debug, error


def process_image_with_template(image_path, template, debug_mode=False):

    log(f"Starting OCR process for image: {image_path}")

    # load image
    image = Image.open(image_path)

    # run OCR on full image once (used by regex / label extractors)
    full_text = pytesseract.image_to_string(image)

    results = {}

    # --------------------------------------------------------
    # Process each field defined in template
    # --------------------------------------------------------
    for field, config in template["fields"].items():

        method = config["extract"]["method"]

        debug(f"Processing field '{field}' using method '{method}'", enabled=debug_mode)

        extractor = EXTRACTORS[method]

        try:

            # bbox extractors operate on image
            if method == "bbox_region":
                raw = extractor(image, config["extract"], debug_mode)

            # regex / label extractors operate on OCR text
            else:
                raw = extractor(full_text, config["extract"])

        except Exception as e:

            error(f"Extraction failed for field '{field}': {e}")
            raw = ""

        # ----------------------------------------------------
        # Clean and validate value
        # ----------------------------------------------------

        field_type = config.get("type", "string")

        cleaned = clean_value(raw, field_type)

        is_valid, value = validate(
            cleaned,
            field_type,
            config.get("validation", {})
        )

        results[field] = value if is_valid else cleaned

        debug(f"Field '{field}' -> {results[field]}", enabled=debug_mode)

    log("OCR processing completed")

    return results