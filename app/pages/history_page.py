from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QLineEdit
)

from PySide6.QtCore import Qt




class HistoryPage(QWidget):


    def __init__(self):

        super().__init__()



        self.conversations = []



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







        self.search_box = QLineEdit()


        self.search_box.setPlaceholderText(
            "🔍 Search history..."
        )


        self.search_box.textChanged.connect(
            self.search_history
        )


        layout.addWidget(
            self.search_box
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







        self.export_button = QPushButton(
            "📄 Export History"
        )


        layout.addWidget(
            self.export_button
        )







        self.setLayout(
            layout
        )









    def update_history(
        self,
        conversations
    ):


        self.conversations = conversations



        self.display_history(
            conversations
        )









    def search_history(self):


        query = self.search_box.text().lower()



        if not query:

            self.display_history(
                self.conversations
            )

            return





        filtered = []



        for item in self.conversations:


            user = item.get(
                "user",
                ""
            ).lower()


            assistant = item.get(
                "assistant",
                ""
            ).lower()



            if query in user or query in assistant:

                filtered.append(
                    item
                )



        self.display_history(
            filtered
        )









    def display_history(
        self,
        conversations
    ):



        if not conversations:


            self.history_label.setText(
                "No conversations found."
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