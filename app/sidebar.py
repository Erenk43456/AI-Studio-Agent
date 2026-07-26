from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QListWidget
)

from PySide6.QtCore import Qt



class Sidebar(QWidget):


    def __init__(self):

        super().__init__()


        self.setFixedWidth(
            180
        )


        self.setStyleSheet(
            """
            QWidget {
                background-color: #181818;
            }


            QPushButton {

                background-color: #252526;
                color: white;
                border: none;
                padding: 12px;
                text-align: left;
                border-radius: 6px;

            }


            QPushButton:hover {

                background-color: #333333;

            }


            QLabel {

                color: white;
                font-size: 16px;
                font-weight:bold;

            }

            """
        )



        layout = QVBoxLayout()



        title = QLabel(
            "🤖 AI-Studio Agent"
        )


        title.setAlignment(
            Qt.AlignCenter
        )


        layout.addWidget(
            title
        )



        layout.addSpacing(
            20
        )



        self.new_chat_button = QPushButton(
            "➕ New Chat"
        )


        self.chat_list = QListWidget()


        self.chat_list.setStyleSheet(
            """
            QListWidget {

                background-color: #202020;
                color: white;
                border: none;

            }


            QListWidget::item {

                padding: 8px;

            }


            QListWidget::item:selected {

                background-color: #333333;

            }

            """
        )



        self.chat_button = QPushButton(
            "💬 Chat"
        )


        self.memory_button = QPushButton(
            "🧠 Memory"
        )


        self.history_button = QPushButton(
            "📜 History"
        )


        self.tools_button = QPushButton(
            "🛠 Tools"
        )


        self.settings_button = QPushButton(
            "⚙ Settings"
        )



        layout.addWidget(
            self.new_chat_button
        )


        layout.addWidget(
            self.chat_list
        )



        layout.addWidget(
            self.chat_button
        )


        layout.addWidget(
            self.memory_button
        )


        layout.addWidget(
            self.history_button
        )


        layout.addWidget(
            self.tools_button
        )


        layout.addWidget(
            self.settings_button
        )



        layout.addStretch()



        self.setLayout(
            layout
        )