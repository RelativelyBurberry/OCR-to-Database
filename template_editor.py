from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QFileDialog, QInputDialog
)
from PySide6.QtGui import QPixmap, QPainter, QPen
from PySide6.QtCore import Qt, QRect
import json
import sys


class ImageCanvas(QLabel):
    def __init__(self):
        super().__init__()
        self.start = None
        self.end = None
        self.boxes = []  # list of (rect, field_name)
        self.pixmap_img = None

    def load_image(self, path):
        # Load original image
        self.original_pixmap = QPixmap(path)

        # Scale image to fit current widget size
        self.display_pixmap = self.original_pixmap.scaled(
            self.width(),
            self.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.setPixmap(self.display_pixmap)

        # 🔑 STORE SCALE FACTORS (THIS IS THE MAGIC)
        self.scale_x = self.original_pixmap.width() / self.display_pixmap.width()
        self.scale_y = self.original_pixmap.height() / self.display_pixmap.height()

        # Resize canvas to displayed image
        self.resize(self.display_pixmap.size())

    def mousePressEvent(self, event):
        self.start = event.position().toPoint()
        self.end = self.start   

    def mouseMoveEvent(self, event):
        self.end = event.position().toPoint()
        self.update()

    def mouseReleaseEvent(self, event):
        self.end = event.position().toPoint()
        rect = QRect(self.start, self.end).normalized()

        field, ok = QInputDialog.getText(
            self, "Field Name", "Enter field name:"
        )
        if ok and field:
            self.boxes.append((rect, field))
        self.start = self.end = None
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        pen = QPen(Qt.red, 2)
        painter.setPen(pen)

        for rect, _ in self.boxes:
            painter.drawRect(rect)

        if self.start and self.end:
            painter.drawRect(QRect(self.start, self.end).normalized())


class TemplateEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Template Editor")
        self.resize(1000, 700)
        self.setMinimumSize(800, 600)

        self.canvas = ImageCanvas()
        self.template = {}

        load_btn = QPushButton("Load Image")
        load_btn.clicked.connect(self.load_image)

        save_btn = QPushButton("Save Template")
        save_btn.clicked.connect(self.save_template)

        layout = QVBoxLayout()
        layout.addWidget(load_btn)
        layout.addWidget(self.canvas, stretch=1)
        layout.addWidget(save_btn)
        self.setLayout(layout)

    def load_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Image")
        if path:
            self.canvas.load_image(path)
            self.image_path = path

    def save_template(self):
        orig_w = self.canvas.original_pixmap.width()
        orig_h = self.canvas.original_pixmap.height()

        fields = {}

        for rect, name in self.canvas.boxes:
            # 🔁 Convert displayed coords → original coords
            orig_x1 = rect.left() * self.canvas.scale_x
            orig_y1 = rect.top() * self.canvas.scale_y
            orig_x2 = rect.right() * self.canvas.scale_x
            orig_y2 = rect.bottom() * self.canvas.scale_y

            # 🔁 Convert to RELATIVE (0–1)
            rel_x1 = orig_x1 / orig_w
            rel_y1 = orig_y1 / orig_h
            rel_x2 = orig_x2 / orig_w
            rel_y2 = orig_y2 / orig_h

            fields[name] = {
                "bbox": [rel_x1, rel_y1, rel_x2, rel_y2],
                "type": "string"  # default
            }

        template = {"fields": fields}

        with open("template.json", "w") as f:
            json.dump(template, f, indent=2)

        print("Template saved as template.json")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = TemplateEditor()
    win.show()
    sys.exit(app.exec())