import sys

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QScrollArea,
    QStackedWidget
)

from PySide6.QtCore import Qt


from tools.tool_registry import ToolRegistry
from tools.calculator import Calculator
from tools.file_tool import FileTool
from tools.memory_tool import MemoryTool


from agents.planner_agent import PlannerAgent
from agents.tool_agent import ToolAgent
from agents.chat_agent import ChatAgent


from memory.memory import Memory
from memory.conversation import ConversationMemory


from app.worker import AIWorker
from app.chat_widget import MessageBubble
from app.header import Header
from app.sidebar import Sidebar


from app.pages.memory_page import MemoryPage
from app.pages.tools_page import ToolsPage
from app.pages.settings_page import SettingsPage




class AIWindow(QWidget):

    def __init__(self):

        super().__init__()


        self.setWindowTitle(
            "AI-Studio-Agent"
        )


        self.resize(
            1000,
            700
        )



        self.setStyleSheet(
            """
            QWidget {
                background-color: #1e1e1e;
                color: white;
            }


            QLineEdit {

                background-color: #252526;
                border: 1px solid #3c3c3c;
                border-radius: 8px;
                padding: 10px;

            }


            QPushButton {

                background-color: #0078d4;
                border-radius: 8px;
                padding: 10px;
                color:white;

            }


            QPushButton:hover {

                background-color:#1084e8;

            }


            QLabel {

                color:white;

            }


            QScrollArea {

                border:none;

            }
            """
        )



        self.busy = False



        #
        # Memory
        #

        self.memory = Memory()

        self.conversation = ConversationMemory()



        #
        # Agents
        #

        self.planner = PlannerAgent(
            self.memory
        )


        registry = ToolRegistry()


        registry.register(
            "calculator",
            Calculator()
        )


        registry.register(
            "file",
            FileTool()
        )


        registry.register(
            "memory",
            MemoryTool(self.memory)
        )



        self.tool_agent = ToolAgent(
            registry,
            self.memory
        )


        self.chat_agent = ChatAgent(
            self.memory
        )



        #
        # Ana düzen
        #

        main_layout = QVBoxLayout()



        self.header = Header()


        main_layout.addWidget(
            self.header
        )



        content_layout = QHBoxLayout()



        #
        # Sidebar
        #

        self.sidebar = Sidebar()


        content_layout.addWidget(
            self.sidebar
        )



        #
        # Sayfalar
        #

        self.pages = QStackedWidget()



        self.chat_widget = QWidget()


        self.chat_layout = QVBoxLayout()



        self.chat_layout.setAlignment(
            Qt.AlignTop
        )



        self.chat_widget.setLayout(
            self.chat_layout
        )


        self.scroll = QScrollArea()


        self.scroll.setWidgetResizable(
            True
        )


        self.scroll.setWidget(
            self.chat_widget
        )


        self.pages.addWidget(
            self.scroll
        )



        self.memory_page = MemoryPage()


        self.tools_page = ToolsPage()


        self.settings_page = SettingsPage()



        self.pages.addWidget(
            self.memory_page
        )


        self.pages.addWidget(
            self.tools_page
        )


        self.pages.addWidget(
            self.settings_page
        )



        content_layout.addWidget(
            self.pages
        )



        main_layout.addLayout(
            content_layout
        )
                #
        # Sidebar bağlantıları
        #

        self.sidebar.chat_button.clicked.connect(
            lambda:
            self.pages.setCurrentIndex(0)
        )


        self.sidebar.memory_button.clicked.connect(
            self.show_memory
        )


        self.sidebar.tools_button.clicked.connect(
            self.show_tools
        )


        self.sidebar.settings_button.clicked.connect(
            lambda:
            self.pages.setCurrentIndex(3)
        )




        #
        # Durum
        #

        self.status = QLabel(
            ""
        )


        self.status.setAlignment(
            Qt.AlignCenter
        )


        main_layout.addWidget(
            self.status
        )




        #
        # Input
        #

        self.input = QLineEdit()


        self.input.returnPressed.connect(
            self.send_message
        )



        self.button = QPushButton(
            "Gönder"
        )


        self.button.clicked.connect(
            self.send_message
        )



        main_layout.addWidget(
            self.input
        )


        main_layout.addWidget(
            self.button
        )



        self.setLayout(
            main_layout
        )





    def show_memory(self):

        self.memory_page.update_memory(
            self.memory.data
        )


        self.pages.setCurrentWidget(
            self.memory_page
        )





    def show_tools(self):

        tools = [
            "calculator",
            "file",
            "memory"
        ]


        self.tools_page.update_tools(
            tools
        )


        self.pages.setCurrentWidget(
            self.tools_page
        )





    def add_message(
        self,
        text,
        is_user
    ):


        bubble = MessageBubble(
            text,
            is_user
        )


        self.chat_layout.addWidget(
            bubble
        )


        self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()
        )





    def send_message(self):


        if self.busy:

            return



        message = self.input.text().strip()


        if not message:

            return



        self.busy = True



        self.button.setEnabled(
            False
        )


        self.input.setEnabled(
            False
        )



        self.add_message(
            message,
            True
        )



        self.input.clear()



        self.status.setText(
            "🤖 AI düşünüyor..."
        )



        self.worker = AIWorker(
            self.planner,
            self.tool_agent,
            self.chat_agent,
            self.conversation,
            message
        )


        self.worker.finished.connect(
            self.show_response
        )


        self.worker.start()





    def show_response(
        self,
        response
    ):


        self.add_message(
            str(response),
            False
        )


        self.status.setText(
            ""
        )


        self.busy = False



        self.button.setEnabled(
            True
        )


        self.input.setEnabled(
            True
        )


        self.input.setFocus()





if __name__ == "__main__":


    app = QApplication(
        sys.argv
    )


    window = AIWindow()


    window.show()


    sys.exit(
        app.exec()
    )