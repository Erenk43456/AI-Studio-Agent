import sys

from PySide6.QtWidgets import QApplication

from app.window.main_window import AIWindow


if __name__ == "__main__":

    app = QApplication(
        sys.argv
    )

    window = AIWindow()

    window.show()

    sys.exit(
        app.exec()
    )