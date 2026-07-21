import sys

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QLineEdit,
    QPushButton
)

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



class AIWindow(QWidget):

    def __init__(self):

        super().__init__()


        self.setWindowTitle(
            "AI-Studio-Agent"
        )


        self.resize(
            600,
            700
        )


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
            MemoryTool(self.memory)
        )


        self.tool_agent = ToolAgent(
            registry,
            self.memory
        )


        self.chat_agent = ChatAgent()



        self.layout = QVBoxLayout()


        self.chat = QTextEdit()

        self.chat.setReadOnly(
            True
        )


        self.input = QLineEdit()


        self.button = QPushButton(
            "Gönder"
        )


        self.button.clicked.connect(
            self.send_message
        )


        self.layout.addWidget(
            self.chat
        )


        self.layout.addWidget(
            self.input
        )


        self.layout.addWidget(
            self.button
        )


        self.setLayout(
            self.layout
        )



    def send_message(self):

        message = self.input.text()


        if not message:
            return


        self.chat.append(
            "Sen: " + message
        )


        self.input.clear()


        self.button.setEnabled(
            False
        )


        self.worker = AIWorker(
            self.planner,
            self.tool_agent,
            self.chat_agent,
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

        self.chat.append(
            "AI: " + response
        )


        self.button.setEnabled(
            True
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