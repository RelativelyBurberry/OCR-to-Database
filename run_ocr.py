import json
import re
from datetime import datetime
from PIL import Image, ImageOps, ImageFilter
import pytesseract
import db

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# ----------------------------
# BBOX CONVERSION
# ----------------------------
def rel_to_abs(rel_bbox, image):
    w, h = image.size
    x1 = int(rel_bbox[0] * w)
    y1 = int(rel_bbox[1] * h)
    x2 = int(rel_bbox[2] * w)
    y2 = int(rel_bbox[3] * h)
    return (x1, y1, x2, y2)


# ----------------------------
# PREPROCESSING
# ----------------------------
def preprocess_for_ocr(img):
    img = img.convert("L")  # grayscale
    img = ImageOps.autocontrast(img)
    img = img.filter(ImageFilter.SHARPEN)
    return img


# ----------------------------
# VALIDATION
# ----------------------------
def validate(value, field_type, rules):
    if value == "":
        return False, "empty"

    try:
        if field_type == "float":
            value = float(value)
        elif field_type == "int":
            value = int(value)
        elif field_type == "string":
            value = value.strip()
    except:
        return False, "type_conversion_failed"

    if "regex" in rules:
        if not re.match(rules["regex"], str(value)):
            return False, "regex_failed"

    if "min" in rules and value < rules["min"]:
        return False, "below_min"

    if "max" in rules and value > rules["max"]:
        return False, "above_max"

    if "min_length" in rules and len(str(value)) < rules["min_length"]:
        return False, "too_short"

    return True, value


# ----------------------------
# VALUE CLEANER
# ----------------------------
def clean_value(raw, field_type):
    raw = raw.strip()

    if field_type == "float":
        cleaned = re.findall(r"\d+\.\d+|\d+", raw)
        return cleaned[0] if cleaned else ""

    if field_type == "int":
        cleaned = re.findall(r"\d+", raw)
        return cleaned[0] if cleaned else ""

    if field_type == "string":
        return " ".join(raw.split())

    return raw


# ----------------------------
# CORE OCR ENGINE (SHARED)
# ----------------------------
def process_image_with_template(image_path, template):
    image = Image.open(image_path)
    results = {}

    for field, data in template["fields"].items():
        bbox = rel_to_abs(data["bbox"], image)
        crop = image.crop(bbox)

        # Preprocess
        crop = preprocess_for_ocr(crop)

        # Upscale small text
        w, h = crop.size
        crop = crop.resize((w * 2, h * 2), Image.BICUBIC)

        raw = pytesseract.image_to_string(
            crop,
            lang="eng",
            config="--psm 7"
        )

        field_type = data.get("type", "string")
        cleaned = clean_value(raw, field_type)

        is_valid, val = validate(
            cleaned,
            field_type,
            data.get("validation", {})
        )

        results[field] = val if is_valid else cleaned

    return results


# ----------------------------
# CLI MAIN
# ----------------------------
def main():
    with open("template.json", "r") as f:
        template = json.load(f)

    results = process_image_with_template("image.png", template)

    print("VALID DATA:")
    print(results)

    print("\nNEEDS REVIEW:")
    print({})  # review removed since shared engine handles validation

    # ---- SAVE TO DB (JSON MODEL) ----
    conn = db.connect()
    db.init_db(conn)

    template_id = template.get("template_id", "default_template")

    existing_id = db.find_compatible_record(conn, template_id, results)

    if existing_id:
        print(f"Compatible record structure exists (id={existing_id}), inserting new row anyway.")

    db.insert_json_record(conn, template_id, results)

    conn.close()
    print("\nSaved to database.")


if __name__ == "__main__":
    main()