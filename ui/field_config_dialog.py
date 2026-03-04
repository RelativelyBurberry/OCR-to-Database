from PySide6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QComboBox,
    QVBoxLayout, QPushButton, QStackedWidget, QSpinBox
)

import re

# simple logger
from utils.logging import log, debug, error


class FieldConfigDialog(QDialog):

    def __init__(self):
        super().__init__()

        log("Opening Field Configuration Dialog")

        self.setWindowTitle("Field Configuration")

        # Default dialog size
        self.resize(420, 300)
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        # ============================================================
        # ===================== FIELD BASIC INFO =====================
        # ============================================================

        # ------------------------------------------------------------
        # Field name input
        # ------------------------------------------------------------

        layout.addWidget(QLabel("Field Name"))

        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        # ------------------------------------------------------------
        # Field type selector
        # Defines how OCR output should be interpreted
        # ------------------------------------------------------------

        layout.addWidget(QLabel("Field Type"))

        self.type_combo = QComboBox()
        self.type_combo.addItems(["string", "int", "float"])

        layout.addWidget(self.type_combo)

        # ------------------------------------------------------------
        # Extraction method selector
        # Determines HOW the value is found in the document
        # ------------------------------------------------------------

        layout.addWidget(QLabel("Extractor"))

        self.extractor_combo = QComboBox()
        self.extractor_combo.addItems([
            "bbox_region",
            "regex",
            "label_nearby"
        ])

        layout.addWidget(self.extractor_combo)

        # ============================================================
        # ================= PARAMETER STACK ==========================
        # ============================================================

        # QStackedWidget lets us swap different parameter panels
        # depending on extractor type
        self.param_stack = QStackedWidget()

        layout.addWidget(self.param_stack)

        # ============================================================
        # ====================== BBOX PANEL ==========================
        # ============================================================

        # Bounding box extraction requires no parameters here
        self.bbox_widget = QLabel("Uses drawn bounding box")

        self.param_stack.addWidget(self.bbox_widget)

        # ============================================================
        # ===================== REGEX BUILDER ========================
        # ============================================================

        regex_layout = QVBoxLayout()

        # ------------------------------------------------------------
        # Literal input
        # Allows adding fixed text segments
        # ------------------------------------------------------------

        regex_layout.addWidget(QLabel("Literal Text"))

        self.literal_input = QLineEdit()

        regex_layout.addWidget(self.literal_input)

        # Auto regex generator
        self.auto_btn = QPushButton("Auto Build From Text")

        regex_layout.addWidget(self.auto_btn)

        self.auto_btn.clicked.connect(self.auto_from_input)

        # Button to add literal segments
        self.add_literal_btn = QPushButton("Add Literal")

        regex_layout.addWidget(self.add_literal_btn)

        # ------------------------------------------------------------
        # Character segment selector
        # ------------------------------------------------------------

        regex_layout.addWidget(QLabel("Character Type"))

        self.char_combo = QComboBox()

        self.char_combo.addItems([
            "Digit",
            "Alphabet",
            "Any"
        ])

        regex_layout.addWidget(self.char_combo)

        # ------------------------------------------------------------
        # Segment repetition count
        # ------------------------------------------------------------

        regex_layout.addWidget(QLabel("Count"))

        self.count_spin = QSpinBox()

        self.count_spin.setMinimum(1)
        self.count_spin.setMaximum(20)

        regex_layout.addWidget(self.count_spin)

        # Button to add dynamic segment
        self.add_segment_btn = QPushButton("Add Segment")

        regex_layout.addWidget(self.add_segment_btn)

        # ------------------------------------------------------------
        # Regex preview elements
        # ------------------------------------------------------------

        self.regex_preview = QLabel("Regex: ")

        regex_layout.addWidget(self.regex_preview)

        self.pattern_view = QLabel("Segments: ")

        regex_layout.addWidget(self.pattern_view)

        # Shows top OCR matches
        self.match_view = QLabel("Matches: ")

        regex_layout.addWidget(self.match_view)

        # container widget
        regex_widget = QLabel()
        regex_widget.setLayout(regex_layout)

        self.param_stack.addWidget(regex_widget)

        # ============================================================
        # =================== REGEX INTERNAL STATE ===================
        # ============================================================

        # Stores regex segments the user builds
        self.pattern_segments = []

        self.add_literal_btn.clicked.connect(self.add_literal)
        self.add_segment_btn.clicked.connect(self.add_segment)

        # ============================================================
        # ====================== LABEL PANEL =========================
        # ============================================================

        # For label-based extraction
        self.label_widget = QLineEdit()

        self.label_widget.setPlaceholderText("Label text")

        self.param_stack.addWidget(self.label_widget)

        # Switch parameter UI based on extractor selection
        self.extractor_combo.currentIndexChanged.connect(self.switch_extractor)

        # ============================================================
        # ======================= SAVE BUTTON ========================
        # ============================================================

        save_btn = QPushButton("Save")

        save_btn.clicked.connect(self.accept)

        layout.addWidget(save_btn)

        self.setLayout(layout)

    # ============================================================
    # =================== CONFIG GENERATION ======================
    # ============================================================

    def get_config(self, bbox):

        log("Generating field configuration")

        name = self.name_input.text()

        field_type = self.type_combo.currentText()

        method = self.extractor_combo.currentText()

        extract = {"method": method}

        if method == "bbox_region":

            extract["bbox"] = bbox

        elif method == "regex":

            extract["pattern"] = self.build_regex()

        elif method == "label_nearby":

            extract["label"] = self.label_widget.text()

        return name, {
            "type": field_type,
            "extract": extract
        }

    # ============================================================
    # ==================== EXTRACTOR SWITCH ======================
    # ============================================================

    def switch_extractor(self, index):

        self.param_stack.setCurrentIndex(index)

        method = self.extractor_combo.currentText()

        debug(f"Extractor switched to {method}", enabled=True)

        # Resize dialog when regex builder is used
        if method == "regex":
            self.resize(500, 500)
        else:
            self.resize(420, 300)

    # ============================================================
    # ===================== REGEX SEGMENTS =======================
    # ============================================================

    def add_literal(self):

        text = self.literal_input.text()

        if not text:
            return

        debug(f"Added literal segment: {text}", enabled=True)

        self.pattern_segments.append({
            "type": "literal",
            "value": text
        })

        self.literal_input.clear()

        self.update_regex()

    def add_segment(self):

        char_type = self.char_combo.currentText()

        count = self.count_spin.value()

        if char_type == "Digit":
            seg_type = "digit"

        elif char_type == "Alphabet":
            seg_type = "alphabet"

        else:
            seg_type = "any"

        debug(f"Added segment {seg_type} x{count}", enabled=True)

        self.pattern_segments.append({
            "type": seg_type,
            "count": count
        })

        self.update_regex()

    # ============================================================
    # ======================= REGEX BUILD ========================
    # ============================================================

    def build_regex(self):

        regex = ""

        for seg in self.pattern_segments:

            if seg["type"] == "literal":
                regex += re.escape(seg["value"])

            elif seg["type"] == "digit":
                regex += f"\\d{{{seg['count']}}}"

            elif seg["type"] == "alphabet":
                regex += f"[A-Za-z]{{{seg['count']}}}"

            elif seg["type"] == "any":
                regex += f".{{{seg['count']}}}"

        debug(f"Built regex: {regex}", enabled=True)

        return regex

    # ============================================================
    # ====================== REGEX PREVIEW =======================
    # ============================================================

    def update_regex(self):

        regex = self.build_regex()

        self.regex_preview.setText(f"Regex: {regex}")

        # Human readable segment preview
        parts = []

        for seg in self.pattern_segments:

            if seg["type"] == "literal":
                parts.append(f"Literal:{seg['value']}")

            elif seg["type"] == "digit":
                parts.append(f"Digit x{seg['count']}")

            elif seg["type"] == "alphabet":
                parts.append(f"Alphabet x{seg['count']}")

            elif seg["type"] == "any":
                parts.append(f"Any x{seg['count']}")

        self.pattern_view.setText("Segments: " + " | ".join(parts))

        # --------------------------------------------------------
        # MATCH PREVIEW FROM OCR TEXT
        # --------------------------------------------------------

        if hasattr(self, "ocr_text") and regex:

            try:

                matches = re.findall(regex, self.ocr_text)

                matches = matches[:3]

                if matches:

                    debug(f"Regex matches found: {matches}", enabled=True)

                    self.match_view.setText("Matches:\n" + "\n".join(matches))

                else:

                    self.match_view.setText("Matches:\nNone")

            except Exception as e:

                error(f"Regex preview failed: {e}")

                self.match_view.setText("Matches:\nInvalid Regex")

    # ============================================================
    # ================= AUTO REGEX GENERATION ====================
    # ============================================================

    def auto_build_from_text(self, text):

        log("Auto generating regex from input")

        self.pattern_segments.clear()

        buffer = ""

        digit_count = 0

        for c in text:

            if c.isdigit():

                digit_count += 1

            else:

                if digit_count > 0:

                    self.pattern_segments.append({
                        "type": "digit",
                        "count": digit_count
                    })

                    digit_count = 0

                buffer += c

        if buffer:

            self.pattern_segments.insert(0, {
                "type": "literal",
                "value": buffer
            })

        if digit_count > 0:

            self.pattern_segments.append({
                "type": "digit",
                "count": digit_count
            })

        self.update_regex()

    def auto_from_input(self):

        text = self.literal_input.text()

        if text:

            debug(f"Auto build triggered for text: {text}", enabled=True)

            self.auto_build_from_text(text)