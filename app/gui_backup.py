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

        self.setup_window()

        self.busy = False

        self.setup_backend()

        self.setup_ui()

        self.connect_events()

        self.show_welcome_message()



    # -------------------------
    # Window
    # -------------------------

    def setup_window(self):

        self.setWindowTitle(
            "AI-Studio-Agent"
        )

        self.resize(
            1000,
            700
        )

        self.setMinimumSize(
            800,
            550
        )


        self.setStyleSheet(
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



    # -------------------------
    # Backend
    # -------------------------

    def setup_backend(self):

        self.memory = Memory()

        self.conversation = ConversationMemory()


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
            MemoryTool(
                self.memory
            )
        )


        self.registry = registry


        self.tool_agent = ToolAgent(
            registry,
            self.memory
        )


        self.chat_agent = ChatAgent(
            self.memory
        )

            # -------------------------
    # UI
    # -------------------------

    def setup_ui(self):

        main_layout = QVBoxLayout()


        self.header = Header()

        main_layout.addWidget(
            self.header
        )


        content_layout = QHBoxLayout()


        self.sidebar = Sidebar()

        content_layout.addWidget(
            self.sidebar
        )


        self.pages = QStackedWidget()


        self.create_chat_page()


        self.memory_page = MemoryPage()

        self.tools_page = ToolsPage()

        self.settings_page = SettingsPage()



        self.pages.addWidget(
            self.scroll
        )


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



        self.status = QLabel(
            "🟢 Ready"
        )


        self.status.setAlignment(
            Qt.AlignCenter
        )


        main_layout.addWidget(
            self.status
        )



        self.input = QLineEdit()


        self.input.setPlaceholderText(
            "Ask something..."
        )


        self.input.returnPressed.connect(
            self.send_message
        )



        self.button = QPushButton(
            "Send"
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




    def create_chat_page(self):

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




    def show_welcome_message(self):

        self.add_message(
            """
🤖 AI-Studio-Agent

Local AI Assistant Ready.

Model: Qwen2.5 Local
Runtime: Ollama

How can I help you?
""",
            False
        )




    # -------------------------
    # Events
    # -------------------------

    def connect_events(self):

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




    # -------------------------
    # Chat
    # -------------------------

    def add_message(
        self,
        text,
        user
    ):

        bubble = MessageBubble(
            text,
            user
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
            "🤖 AI Thinking..."
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
            "🟢 Ready"
        )


        self.busy = False


        self.button.setEnabled(
            True
        )


        self.input.setEnabled(
            True
        )


        self.input.setFocus()




    # -------------------------
    # Pages
    # -------------------------

    def show_memory(self):

        self.memory_page.update_memory(
            self.memory.data
        )


        self.pages.setCurrentWidget(
            self.memory_page
        )




    def show_tools(self):

        self.tools_page.update_tools(
            self.registry.list_tools()
        )


        self.pages.setCurrentWidget(
            self.tools_page
        )





if __name__ == "__main__":


    app = QApplication(
        sys.argv
    )


    window = AIWindow()


    window.show()


    sys.exit(
        app.exec()
    )