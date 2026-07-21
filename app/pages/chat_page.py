from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class ChatPage(QWidget):

    def __init__(self):

        super().__init__()


        layout = QVBoxLayout()


        label = QLabel(
            "💬 Sohbet"
        )


        label.setStyleSheet(
            """
            QLabel {
                font-size:18px;
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