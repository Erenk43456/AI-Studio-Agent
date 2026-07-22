from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea
)

from PySide6.QtCore import Qt





class ChatUI:



    @staticmethod
    def create(window):


        window.chat_widget = QWidget()



        window.chat_layout = QVBoxLayout()



        window.chat_layout.setSpacing(
            12
        )



        window.chat_layout.setContentsMargins(
            10,
            10,
            10,
            10
        )



        window.chat_layout.setAlignment(
            Qt.AlignTop
        )



        window.chat_widget.setLayout(
            window.chat_layout
        )



        window.scroll = QScrollArea()



        window.scroll.setWidgetResizable(
            True
        )



        window.scroll.setWidget(
            window.chat_widget
        )