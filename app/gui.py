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


        self.setStyleSheet("""
        QWidget {
            background-color: #1e1e1e;
            color: white;
        }

        QTextEdit {
            background-color: #252526;
            border: 1px solid #3c3c3c;
            border-radius: 8px;
            padding: 10px;
            font-size: 14px;
        }

        QLineEdit {
            background-color: #252526;
            border: 1px solid #3c3c3c;
            border-radius: 8px;
            padding: 10px;
            font-size: 14px;
        }

        QPushButton {
            background-color: #0078d4;
            border-radius: 8px;
            padding: 10px;
        }

        QPushButton:hover {
            background-color: #1084e8;
        }
        """)


        self.busy = False


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



        layout = QVBoxLayout()


        self.chat = QTextEdit()

        self.chat.setReadOnly(
            True
        )


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


        layout.addWidget(
            self.chat
        )

        layout.addWidget(
            self.input
        )

        layout.addWidget(
            self.button
        )


        self.setLayout(
            layout
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


        self.chat.append(
            "Sen: " + message
        )


        self.input.clear()



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
            "AI: " + str(response)
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