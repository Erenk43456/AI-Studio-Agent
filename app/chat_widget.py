from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout
)

from PySide6.QtCore import Qt



class MessageBubble(QWidget):

    def __init__(
        self,
        text,
        is_user=False
    ):

        super().__init__()


        layout = QHBoxLayout()


        self.label = QLabel(
            text
        )


        self.label.setWordWrap(
            True
        )


        self.label.setMaximumWidth(
            450
        )


        self.label.setStyleSheet(
            """
            QLabel {
                padding: 10px;
                border-radius: 12px;
                font-size: 14px;
            }
            """
        )



        if is_user:

            self.label.setStyleSheet(
                """
                QLabel {
                    background-color: #0078d4;
                    color: white;
                    padding: 10px;
                    border-radius: 12px;
                }
                """
            )

            layout.addStretch()

            layout.addWidget(
                self.label
            )


        else:

            self.label.setStyleSheet(
                """
                QLabel {
                    background-color: #333333;
                    color: white;
                    padding: 10px;
                    border-radius: 12px;
                }
                """
            )

            layout.addWidget(
                self.label
            )

            layout.addStretch()



        self.setLayout(
            layout
        )