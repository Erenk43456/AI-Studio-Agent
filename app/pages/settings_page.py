from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class SettingsPage(QWidget):

    def __init__(self):

        super().__init__()


        layout = QVBoxLayout()


        label = QLabel(
    """
⚙ Settings


Model:
Qwen2.5:3B


Runtime:
Local AI


Server:
localhost:11434
"""
        )


        label.setStyleSheet(
            """
            QLabel {
                font-size:16px;
                color:white;
            }
            """
        )


        layout.addWidget(
            label
        )


        self.setLayout(
            layout
        )