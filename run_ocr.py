import json
from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def rel_to_abs(rel_bbox, image):
    w, h = image.size
    x1 = int(rel_bbox[0] * w)
    y1 = int(rel_bbox[1] * h)
    x2 = int(rel_bbox[2] * w)
    y2 = int(rel_bbox[3] * h)
    return (x1, y1, x2, y2)

# ---- MAIN ----

image = Image.open("image.png")

with open("template.json", "r") as f:
    template = json.load(f)

results = {}

for field_name, field_data in template["fields"].items():
    bbox = rel_to_abs(field_data["bbox"], image)
    crop = image.crop(bbox)
    crop.show()

    text = pytesseract.image_to_string(crop, lang="eng").strip()
    results[field_name] = text

print(results)