from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QWidget, QPushButton, QLabel,
    QVBoxLayout, QFileDialog, QFormLayout, QLineEdit,
    QRadioButton, QButtonGroup, QCheckBox, QTabWidget, QTextEdit
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from ui.template_editor import TemplateEditor

import sys
import os

# Template loading utilities
from utils.config_loader import list_templates, load_template

# OCR engine
from ocr_core.engine import process_image_with_template

# Database adapter
from db import db as db

# Simple logger
from utils.logging import log, debug, error

import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Directory where template JSON files live
TEMPLATE_DIR = os.path.join("configs", "templates")


class OCRApp(QWidget):

    def __init__(self):
        super().__init__()

        log("Starting OCR Application UI")

        self.setWindowTitle("OCR App")

        self.resize(1100, 800)
        self.setMinimumSize(900, 650)

        # ============================================================
        # ======================== TABS ===============================
        # ============================================================

        # QTabWidget allows multiple pages inside one window
        self.tabs = QTabWidget()

        self.ocr_tab = QWidget()
        self.logs_tab = QWidget()

        self.tabs.addTab(self.ocr_tab, "OCR")
        self.tabs.addTab(self.logs_tab, "Logs")

        # Main window layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)

        self.setLayout(main_layout)

        # ============================================================
        # ====================== STATE VARIABLES =====================
        # ============================================================

        self.image_path = None   # currently loaded image
        self.inputs = {}         # form fields for OCR results

        # ============================================================
        # ======================= LOGS TAB ===========================
        # ============================================================

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)  # prevents user editing

        self.clear_logs_btn = QPushButton("Clear Logs")
        self.clear_logs_btn.clicked.connect(self.clear_logs)

        # Refresh logs whenever user switches to logs tab
        self.tabs.currentChanged.connect(self.on_tab_change)

        logs_layout = QVBoxLayout(self.logs_tab)
        logs_layout.addWidget(self.log_box)
        logs_layout.addWidget(self.clear_logs_btn)

        # ============================================================
        # ======================= OCR TAB ============================
        # ============================================================

        # Layout attached directly to OCR tab
        self.layout = QVBoxLayout(self.ocr_tab)

        # ------------------------------------------------------------
        # Top bar (Debug toggle)
        # ------------------------------------------------------------

        top_bar = QHBoxLayout()
        top_bar.addStretch()  # pushes checkbox to right side

        self.debug_checkbox = QCheckBox("Debug Mode")
        top_bar.addWidget(self.debug_checkbox)

        self.layout.addLayout(top_bar)

        # ------------------------------------------------------------
        # Image preview
        # ------------------------------------------------------------

        self.image_label = QLabel("No image loaded")
        self.image_label.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.image_label)

        # ------------------------------------------------------------
        # Template editor button
        # ------------------------------------------------------------

        self.edit_template_btn = QPushButton("Edit Template")
        self.edit_template_btn.clicked.connect(self.open_template_editor)

        self.layout.addWidget(self.edit_template_btn)

        # ------------------------------------------------------------
        # Template selector (radio buttons)
        # ------------------------------------------------------------

        self.template_group = QButtonGroup(self)

        self.template_buttons_layout = QVBoxLayout()
        self.layout.addLayout(self.template_buttons_layout)

        self.load_templates()

        # ------------------------------------------------------------
        # Image loading button
        # ------------------------------------------------------------

        self.load_btn = QPushButton("Load Image")
        self.load_btn.clicked.connect(self.load_image)

        self.layout.addWidget(self.load_btn)

        # ------------------------------------------------------------
        # OCR execution button
        # ------------------------------------------------------------

        self.extract_btn = QPushButton("Run OCR")
        self.extract_btn.clicked.connect(self.run_ocr)

        self.layout.addWidget(self.extract_btn)

        # ------------------------------------------------------------
        # Form layout (shows extracted fields)
        # ------------------------------------------------------------

        self.form = QFormLayout()
        self.layout.addLayout(self.form)

        # ------------------------------------------------------------
        # Save results button
        # ------------------------------------------------------------

        self.save_btn = QPushButton("Save to DB")
        self.save_btn.clicked.connect(self.save)

        self.layout.addWidget(self.save_btn)

    # ============================================================
    # ===================== TEMPLATE LOADING =====================
    # ============================================================

    def load_templates(self):

        log("Loading template list")

        # Remove previous buttons
        for i in reversed(range(self.template_buttons_layout.count())):
            widget = self.template_buttons_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        self.template_group = QButtonGroup(self)

        files = list_templates()

        for i, name in enumerate(files):

            btn = QRadioButton(name)

            # Select first template automatically
            if i == 0:
                btn.setChecked(True)

            self.template_group.addButton(btn)
            self.template_buttons_layout.addWidget(btn)

        debug(f"{len(files)} templates loaded", enabled=True)

    # ============================================================
    # ==================== TEMPLATE EDITOR =======================
    # ============================================================

    def open_template_editor(self):

        log("Opening template editor")

        self.editor = TemplateEditor()

        # Reload templates after user saves a new one
        self.editor.template_saved.connect(self.reload_template)

        self.editor.show()

    def reload_template(self):

        log("Reloading templates")

        self.load_templates()

    # ============================================================
    # ====================== IMAGE LOADING =======================
    # ============================================================

    def load_image(self):

        path, _ = QFileDialog.getOpenFileName(self, "Select Image")

        if path:

            log(f"Image loaded: {path}")

            self.image_path = path

            pix = QPixmap(path).scaled(400, 500, Qt.KeepAspectRatio)

            self.image_label.setPixmap(pix)

    # ============================================================
    # ======================= RUN OCR ============================
    # ============================================================

    def run_ocr(self):

        if not self.image_path:

            error("OCR attempted with no image loaded")

            return

        log("Starting OCR process")

        # Get selected template
        selected_button = self.template_group.checkedButton()

        if not selected_button:

            error("No template selected")

            return

        template_name = selected_button.text()

        debug(f"Using template: {template_name}", enabled=True)

        # Load template configuration
        self.template = load_template(template_name)

        # Clear previous form
        for i in reversed(range(self.form.rowCount())):
            self.form.removeRow(i)

        self.inputs.clear()

        debug_mode = self.debug_checkbox.isChecked()

        try:

            results = process_image_with_template(
                self.image_path,
                self.template,
                debug_mode=debug_mode
            )

            log("OCR processing completed")

        except Exception as e:

            error(f"OCR failed: {e}")
            return

        # Display results in editable form
        for field, value in results.items():

            entry = QLineEdit()

            entry.setText(str(value))

            self.form.addRow(field, entry)

            self.inputs[field] = entry

        self.refresh_logs()

    # ============================================================
    # ====================== DATABASE SAVE =======================
    # ============================================================

    def save(self):

        log("Saving OCR results to database")

        results = {k: v.text() for k, v in self.inputs.items()}

        try:

            conn = db.connect()

            db.init_db(conn)

            template_id = self.template.get("template_id", "default_template")

            db.insert_json_record(conn, template_id, results)

            conn.close()

            log("Database save successful")

        except Exception as e:

            error(f"Database save failed: {e}")

        self.image_label.setText("Saved successfully ✔")

        self.refresh_logs()

    # ============================================================
    # ======================== LOG VIEW ==========================
    # ============================================================

    def refresh_logs(self):

        try:

            with open("logs/app.log", "r", encoding="utf-8") as f:

                self.log_box.setPlainText(f.read())

                # auto scroll to bottom
                scrollbar = self.log_box.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())

        except:

            self.log_box.setPlainText("No logs yet.")

    # ============================================================
    # ======================= CLEAR LOGS =========================
    # ============================================================

    def clear_logs(self):

        log("Logs cleared by user")

        os.makedirs("logs", exist_ok=True)

        open("logs/app.log", "w").close()

        self.refresh_logs()

    # ============================================================
    # ====================== TAB SWITCHING =======================
    # ============================================================

    def on_tab_change(self, index):

        # If user switches to logs tab, refresh logs
        if self.tabs.tabText(index) == "Logs":

            self.refresh_logs()


# ============================================================
# ====================== APPLICATION START ===================
# ============================================================

if __name__ == "__main__":

    log("Launching OCR application")

    app = QApplication(sys.argv)

    window = OCRApp()

    window.show()

    sys.exit(app.exec())