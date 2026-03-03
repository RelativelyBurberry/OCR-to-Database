from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QVBoxLayout, QFileDialog, QFormLayout, QLineEdit
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from template_editor import TemplateEditor
import sys

# import your existing logic
import json
from PIL import Image
import pytesseract
import db
from run_ocr import rel_to_abs, clean_value, validate
from run_ocr import process_image_with_template

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


class OCRApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BBox OCR App")

        self.resize(1100, 800)
        self.setMinimumSize(900, 650)

        self.image_path = None
        self.inputs = {}

        self.layout = QVBoxLayout()

        self.image_label = QLabel("No image loaded")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.image_label)

        self.edit_template_btn = QPushButton("Edit Template")
        self.edit_template_btn.clicked.connect(self.open_template_editor)
        self.layout.addWidget(self.edit_template_btn)

        self.load_btn = QPushButton("Load Image")
        self.load_btn.clicked.connect(self.load_image)
        self.layout.addWidget(self.load_btn)

        self.extract_btn = QPushButton("Run OCR")
        self.extract_btn.clicked.connect(self.run_ocr)
        self.layout.addWidget(self.extract_btn)

        self.form = QFormLayout()
        self.layout.addLayout(self.form)

        self.save_btn = QPushButton("Save to DB")
        self.save_btn.clicked.connect(self.save)
        self.layout.addWidget(self.save_btn)

        self.setLayout(self.layout)

        with open("template.json") as f:
            self.template = json.load(f)
    
    def open_template_editor(self):
        self.editor = TemplateEditor()
        self.editor.show()
        self.editor.destroyed.connect(self.reload_template)

    def load_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Image")
        if path:
            self.image_path = path
            pix = QPixmap(path).scaled(400, 500, Qt.KeepAspectRatio)
            self.image_label.setPixmap(pix)
    
    def reload_template(self):
        with open("template.json") as f:
            self.template = json.load(f)

    def run_ocr(self):
        if not self.image_path:
            return

        image = Image.open(self.image_path)

        # clear previous inputs
        for i in reversed(range(self.form.rowCount())):
            self.form.removeRow(i)
        self.inputs.clear()

        for field, data in self.template["fields"].items():
            bbox = rel_to_abs(data["bbox"], image)
            crop = image.crop(bbox)

            raw = pytesseract.image_to_string(crop)
            field_type = data.get("type", "string")
            cleaned = clean_value(raw, field_type)

            is_valid, val = validate(
                cleaned,
                data["type"],
                data.get("validation", {})
            )

            entry = QLineEdit()
            entry.setText(str(val if is_valid else cleaned))
            self.form.addRow(field, entry)
            self.inputs[field] = entry

    def save(self):
        results = {k: v.text() for k, v in self.inputs.items()}

        conn = db.connect()
        schema = {
            fname: fdata["type"]
            for fname, fdata in self.template["fields"].items()
        }
        db.create_table(conn, "records", schema)
        db.insert_row(conn, "records", results)

        self.image_label.setText("Saved successfully ✔")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OCRApp()
    window.show()
    sys.exit(app.exec())