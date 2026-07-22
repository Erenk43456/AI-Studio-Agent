from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton
)

from PySide6.QtCore import Qt


from app.header import Header
from app.sidebar import Sidebar


from app.ui.styles import AppStyles
from app.ui.chat_ui import ChatUI
from app.ui.page_manager import PageManager





class UIBuilder:



    @staticmethod
    def setup_window(window):


        window.setWindowTitle(
            "AI-Studio-Agent"
        )


        window.resize(
            1000,
            700
        )


        window.setMinimumSize(
            800,
            550
        )


        window.setStyleSheet(
            AppStyles.MAIN_STYLE
        )







    @staticmethod
    def build(window):


        main_layout = QVBoxLayout()



        window.header = Header()


        main_layout.addWidget(
            window.header
        )



        content_layout = QHBoxLayout()



        window.sidebar = Sidebar()


        content_layout.addWidget(
            window.sidebar
        )




        #
        # Chat UI
        #

        ChatUI.create(
            window
        )



        #
        # Pages
        #

        PageManager.create(
            window
        )



        content_layout.addWidget(
            window.pages
        )



        main_layout.addLayout(
            content_layout
        )





        #
        # Status
        #

        window.status = QLabel(
            "🟢 Ready"
        )


        window.status.setAlignment(
            Qt.AlignCenter
        )


        main_layout.addWidget(
            window.status
        )





        #
        # Input
        #

        window.input = QLineEdit()


        window.input.setPlaceholderText(
            "Ask something..."
        )



        window.button = QPushButton(
            "Send"
        )



        main_layout.addWidget(
            window.input
        )


        main_layout.addWidget(
            window.button
        )



        window.setLayout(
            main_layout
        )