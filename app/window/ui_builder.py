from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QWidget
)

from PySide6.QtCore import Qt



from app.header import Header
from app.sidebar import Sidebar

from app.chat_widget import MessageBubble

from app.pages.memory_page import MemoryPage
from app.pages.history_page import HistoryPage
from app.pages.tools_page import ToolsPage
from app.pages.settings_page import SettingsPage





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
            """
            QWidget {
                background-color:#1e1e1e;
                color:white;
            }


            QLineEdit {

                background:#252526;
                border:1px solid #3c3c3c;
                border-radius:8px;
                padding:10px;

            }


            QPushButton {

                background:#0078d4;
                border-radius:8px;
                padding:10px;

            }


            QPushButton:hover {

                background:#1084e8;

            }


            QScrollArea {

                border:none;

            }
            """
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



        window.pages = QStackedWidget()



        UIBuilder.create_chat_page(
            window
        )



        window.memory_page = MemoryPage()

        window.history_page = HistoryPage()

        window.tools_page = ToolsPage()

        window.settings_page = SettingsPage()



        window.pages.addWidget(
            window.scroll
        )


        window.pages.addWidget(
            window.memory_page
        )


        window.pages.addWidget(
            window.history_page
        )


        window.pages.addWidget(
            window.tools_page
        )


        window.pages.addWidget(
            window.settings_page
        )



        content_layout.addWidget(
            window.pages
        )



        main_layout.addLayout(
            content_layout
        )



        window.status = QLabel(
            "🟢 Ready"
        )


        window.status.setAlignment(
            Qt.AlignCenter
        )


        main_layout.addWidget(
            window.status
        )



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





    @staticmethod
    def create_chat_page(window):


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