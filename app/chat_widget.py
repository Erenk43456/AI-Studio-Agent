from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout
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


        layout.setContentsMargins(
            10,
            5,
            10,
            5
        )

        layout.setSpacing(
            0
        )


        self.label = QLabel(
            text
        )


        self.label.setWordWrap(
            True
        )


        self.label.setTextInteractionFlags(
            Qt.TextSelectableByMouse
        )


        self.label.setMaximumWidth(
            600
        )


        if is_user:


            self.label.setStyleSheet(
                """
                QLabel {

                    background-color:#0078d4;

                    color:white;

                    padding:12px;

                    border-radius:14px;

                    font-size:14px;

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

                    background-color:#333333;

                    color:white;

                    padding:12px;

                    border-radius:14px;

                    font-size:14px;

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