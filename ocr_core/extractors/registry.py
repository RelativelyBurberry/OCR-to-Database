# ============================================================
# EXTRACTOR REGISTRY
# Maps extractor names → extraction functions
# ============================================================

from .bbox import extract_bbox
from .regex import extract_regex
from .label_nearby import extract_label_nearby

from utils.logging import debug


# dictionary used by OCR engine to select extraction method
EXTRACTORS = {

    "bbox_region": extract_bbox,

    "regex": extract_regex,

    "label_nearby": extract_label_nearby
}


# ------------------------------------------------------------
# Helper (optional): get extractor by name
# ------------------------------------------------------------
def get_extractor(method):

    extractor = EXTRACTORS.get(method)

    debug(f"Extractor requested: {method}", enabled=True)

    return extractor