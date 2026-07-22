from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel
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