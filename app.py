# ============================================================
# APPLICATION ENTRY POINT
# Launches the OCR desktop application
# ============================================================

from PySide6.QtWidgets import QApplication
from ui.main import OCRApp
from utils.logging import log, error

import sys

def main():
    log("Starting OCR Application")
    try:
        app = QApplication(sys.argv)
        window = OCRApp()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        error(f"Application failed to start: {e}")


if __name__ == "__main__":
    main()