# ============================================================
# OCR PREPROCESSING
# Improves image quality before passing to Tesseract
# ============================================================

from PIL import ImageOps, ImageFilter
from utils.logging import debug


def preprocess_for_ocr(img):
    """
    Basic preprocessing pipeline:
    - convert to grayscale
    - improve contrast
    - sharpen text edges
    """

    debug("Running OCR preprocessing", enabled=True)

    img = img.convert("L")  # convert to grayscale
    img = ImageOps.autocontrast(img)  # normalize contrast
    img = img.filter(ImageFilter.SHARPEN)  # sharpen edges
    img = img.point(lambda x: 0 if x < 140 else 255) # binarize (thresholding)

    return img