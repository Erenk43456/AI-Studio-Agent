from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea
)

from PySide6.QtCore import Qt



class HistoryPage(QWidget):


    def __init__(self):

        super().__init__()


        layout = QVBoxLayout()



        title = QLabel(
            "📜 Conversation History"
        )


        title.setStyleSheet(
            """
            QLabel {
                font-size:20px;
                font-weight:bold;
                color:white;
            }
            """
        )


        layout.addWidget(
            title
        )




        self.history_label = QLabel(
            "No conversations yet."
        )


        self.history_label.setAlignment(
            Qt.AlignTop
        )


        self.history_label.setWordWrap(
            True
        )


        self.history_label.setStyleSheet(
            """
            QLabel {

                font-size:15px;
                color:white;

            }
            """
        )



        self.scroll = QScrollArea()


        self.scroll.setWidgetResizable(
            True
        )


        self.scroll.setWidget(
            self.history_label
        )



        layout.addWidget(
            self.scroll
        )





        self.clear_button = QPushButton(
            "🗑 Clear History"
        )


        layout.addWidget(
            self.clear_button
        )



        self.setLayout(
            layout
        )





    def update_history(
        self,
        conversations
    ):


        if not conversations:

            self.history_label.setText(
                "No conversations yet."
            )

            return



        text = "📜 Conversation History\n\n"



        for item in reversed(
            conversations
        ):


            user = item.get(
                "user",
                ""
            )


            assistant = item.get(
                "assistant",
                ""
            )


            time = item.get(
                "time",
                ""
            )



            text += (
                f"🕒 {time}\n\n"
                f"👤 User:\n{user}\n\n"
                f"🤖 AI:\n{assistant}\n"
                f"\n----------------------\n\n"
            )



        self.history_label.setText(
            text
        )