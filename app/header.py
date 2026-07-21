from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel
)

from PySide6.QtCore import Qt



class Header(QWidget):

    def __init__(self):

        super().__init__()



        layout = QVBoxLayout()



        self.title = QLabel(
            "🤖 AI-Studio-Agent"
        )


        self.title.setAlignment(
            Qt.AlignCenter
        )


        self.title.setStyleSheet(
            """
            QLabel {
                color: white;
                font-size: 22px;
                font-weight: bold;
                padding: 8px;
            }
            """
        )



        self.model = QLabel(
            "Qwen2.5:3b • Local AI Model"
        )


        self.model.setAlignment(
            Qt.AlignCenter
        )


        self.model.setStyleSheet(
            """
            QLabel {
                color: #aaaaaa;
                font-size: 12px;
                padding-bottom: 8px;
            }
            """
        )



        layout.addWidget(
            self.title
        )


        layout.addWidget(
            self.model
        )



        self.setLayout(
            layout
        )