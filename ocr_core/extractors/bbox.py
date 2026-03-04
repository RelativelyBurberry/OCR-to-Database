# ============================================================
# BBOX EXTRACTION
# Extracts OCR text from a bounding box region of an image
# ============================================================

import pytesseract
from PIL import Image

from ocr_core.preprocess import preprocess_for_ocr
from utils.logging import log, debug, error


# ------------------------------------------------------------
# Convert relative bbox (0–1) → absolute pixel coordinates
# ------------------------------------------------------------
def rel_to_abs(rel_bbox, image):

    w, h = image.size

    x1 = int(rel_bbox[0] * w)
    y1 = int(rel_bbox[1] * h)
    x2 = int(rel_bbox[2] * w)
    y2 = int(rel_bbox[3] * h)

    return (x1, y1, x2, y2)


# ------------------------------------------------------------
# Run OCR on a bounding box region
# ------------------------------------------------------------
def extract_bbox(image, field_config, debug_mode=False):

    log("Running bbox OCR extraction")

    # convert relative bbox → absolute pixels
    bbox = rel_to_abs(field_config["bbox"], image)

    crop = image.crop(bbox)

    if debug_mode:
        crop.show()
        debug(f"BBOX crop: {bbox}", enabled=True)

    # preprocess for better OCR
    crop = preprocess_for_ocr(crop)

    # upscale small text regions (improves OCR accuracy)
    w, h = crop.size
    crop = crop.resize((w * 2, h * 2), Image.BICUBIC)

    try:
        raw = pytesseract.image_to_string(
            crop,
            lang="eng",
            config="--psm 7"
        )

        debug(f"OCR result: {raw}", enabled=debug)

        return raw

    except Exception as e:

        error(f"OCR extraction failed: {e}")
        return ""