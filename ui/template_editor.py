from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QFileDialog, QInputDialog, QLineEdit
)
from PySide6.QtGui import QPixmap, QPainter, QPen
from PySide6.QtCore import Qt, QRect, Signal

import json
import sys
import os

from PIL import Image
import pytesseract

# project logger
from utils.logging import log, debug, error


# Directory where template JSON files are stored
TEMPLATE_DIR = os.path.join("configs", "templates")


# ============================================================
# ====================== IMAGE CANVAS ========================
# ============================================================
# Custom QLabel that allows users to draw bounding boxes
# on the image to mark fields for OCR extraction
# ============================================================

class ImageCanvas(QLabel):

    def __init__(self):
        super().__init__()

        # start and end coordinates while dragging
        self.start = None
        self.end = None

        # stores all drawn bounding boxes
        # format: (QRect, field_name, config)
        self.boxes = []

        self.pixmap_img = None

    # ========================================================
    # ================= IMAGE LOADING ========================
    # ========================================================

    def load_image(self, path):

        log(f"Template editor image loaded: {path}")

        # Load original image
        self.original_pixmap = QPixmap(path)
        self.image_path = path

        # Scale image to fit the widget
        self.update_display_pixmap()

        # store scale factors (display image -> original image)
        self.scale_x = self.original_pixmap.width() / self.display_pixmap.width()
        self.scale_y = self.original_pixmap.height() / self.display_pixmap.height()

        # resize canvas to match image size
        self.resize(self.display_pixmap.size())

    # ========================================================
    # =============== DISPLAY IMAGE SCALING ==================
    # ========================================================

    def update_display_pixmap(self):

        # prevents crashes if image not loaded
        if not hasattr(self, "original_pixmap"):
            return

        # ensure widget always has non-zero size
        w = max(self.width(), 1)
        h = max(self.height(), 1)

        # scale image while preserving aspect ratio
        self.display_pixmap = self.original_pixmap.scaled(
            w,
            h,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.setPixmap(self.display_pixmap)

        # update scale factors
        self.scale_x = self.original_pixmap.width() / self.display_pixmap.width()
        self.scale_y = self.original_pixmap.height() / self.display_pixmap.height()

        self.resize(self.display_pixmap.size())

    # triggered whenever window is resized
    def resizeEvent(self, event):
        self.update_display_pixmap()
        super().resizeEvent(event)

    # ========================================================
    # ==================== MOUSE EVENTS ======================
    # ========================================================
    # These allow the user to drag a rectangle to mark fields
    # ========================================================

    def mousePressEvent(self, event):

        # start drawing
        self.start = event.position().toPoint()
        self.end = self.start

    def mouseMoveEvent(self, event):

        # update rectangle as mouse moves
        self.end = event.position().toPoint()
        self.update()

    def mouseReleaseEvent(self, event):

        # finish rectangle drawing
        self.end = event.position().toPoint()

        rect = QRect(self.start, self.end).normalized()

        debug(f"Bounding box drawn: {rect}", enabled=True)

        # open field configuration dialog
        from ui.field_config_dialog import FieldConfigDialog

        dialog = FieldConfigDialog()

        # run OCR on image to allow regex preview
        if hasattr(self, "image_path"):
            img = Image.open(self.image_path)
            dialog.ocr_text = pytesseract.image_to_string(img)

        # user configures field
        if dialog.exec():

            name, config = dialog.get_config(None)

            log(f"Field created: {name}")

            self.boxes.append((rect, name, config))

        # reset drag state
        self.start = self.end = None
        self.update()

    # ========================================================
    # ==================== DRAW BOXES ========================
    # ========================================================
    # Paint event draws bounding boxes on the image
    # ========================================================

    def paintEvent(self, event):

        super().paintEvent(event)

        painter = QPainter(self)

        # red outline boxes
        pen = QPen(Qt.red, 2)
        painter.setPen(pen)

        # draw saved boxes
        for rect, _, _ in self.boxes:
            painter.drawRect(rect)

        # draw current box while dragging
        if self.start and self.end:
            painter.drawRect(QRect(self.start, self.end).normalized())


# ============================================================
# ===================== TEMPLATE EDITOR ======================
# ============================================================
# GUI for creating new OCR templates
# Users load an image and mark extraction regions
# ============================================================

class TemplateEditor(QWidget):

    template_saved = Signal()

    def __init__(self):
        super().__init__()

        log("Opening Template Editor")

        self.setWindowTitle("Template Editor")

        self.resize(1000, 700)
        self.setMinimumSize(800, 600)

        # ----------------------------------------------------
        # Canvas for drawing bounding boxes
        # ----------------------------------------------------

        self.canvas = ImageCanvas()

        # ----------------------------------------------------
        # Template name input
        # ----------------------------------------------------

        self.template_name_input = QLineEdit()
        self.template_name_input.setPlaceholderText("Enter Template Name")

        # ----------------------------------------------------
        # Buttons
        # ----------------------------------------------------

        load_btn = QPushButton("Load Image")
        load_btn.clicked.connect(self.load_image)

        save_btn = QPushButton("Save Template")
        save_btn.clicked.connect(self.save_template)

        # ----------------------------------------------------
        # Layout
        # ----------------------------------------------------

        layout = QVBoxLayout()

        layout.addWidget(self.template_name_input)
        layout.addWidget(load_btn)

        # canvas expands to fill available space
        layout.addWidget(self.canvas, stretch=1)

        layout.addWidget(save_btn)

        self.setLayout(layout)

    # ========================================================
    # =================== IMAGE LOADING ======================
    # ========================================================

    def load_image(self):

        path, _ = QFileDialog.getOpenFileName(self, "Select Image")

        if path:

            log(f"Template editor image selected: {path}")

            self.canvas.load_image(path)
            self.image_path = path

    # ========================================================
    # ================= TEMPLATE SAVE ========================
    # ========================================================

    def save_template(self):

        log("Saving template")

        if not hasattr(self.canvas, "original_pixmap"):

            error("Template save attempted without image")

            print("Load an image first.")
            return

        orig_w = self.canvas.original_pixmap.width()
        orig_h = self.canvas.original_pixmap.height()

        fields = {}

        # convert each bounding box into template config
        for rect, name, config in self.canvas.boxes:

            # convert from displayed image coords → original image coords
            orig_x1 = rect.left() * self.canvas.scale_x
            orig_y1 = rect.top() * self.canvas.scale_y
            orig_x2 = rect.right() * self.canvas.scale_x
            orig_y2 = rect.bottom() * self.canvas.scale_y

            # convert to relative coordinates (0-1 range)
            rel_x1 = orig_x1 / orig_w
            rel_y1 = orig_y1 / orig_h
            rel_x2 = orig_x2 / orig_w
            rel_y2 = orig_y2 / orig_h

            if config["extract"]["method"] == "bbox_region":

                config["extract"]["bbox"] = [
                    rel_x1,
                    rel_y1,
                    rel_x2,
                    rel_y2
                ]

            fields[name] = config

        template_name = self.template_name_input.text().strip()

        if not template_name:

            error("Template save failed: missing template name")

            print("Template name required!")
            return

        template = {
            "template_id": template_name,
            "fields": fields
        }

        # ensure template directory exists
        os.makedirs(TEMPLATE_DIR, exist_ok=True)

        path = os.path.join(TEMPLATE_DIR, f"{template_name}.json")

        with open(path, "w") as f:
            json.dump(template, f, indent=2)

        log(f"Template saved: {path}")

        print(f"Template saved as {path}")

        # notify main UI that template list should refresh
        self.template_saved.emit()

        self.close()


# ============================================================
# =================== STANDALONE RUN =========================
# ============================================================

if __name__ == "__main__":

    log("Launching Template Editor standalone")

    app = QApplication(sys.argv)

    win = TemplateEditor()
    win.show()

    sys.exit(app.exec())