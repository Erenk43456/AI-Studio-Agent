from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QScrollArea,
    QPushButton
)

from PySide6.QtCore import Qt




class MemoryPage(QWidget):


    def __init__(self):

        super().__init__()



        layout = QVBoxLayout()






        title = QLabel(
            "🧠 Memory System"
        )



        title.setStyleSheet(
            """
            QLabel {
                font-size:22px;
                font-weight:bold;
                color:white;
            }
            """
        )



        layout.addWidget(
            title
        )








        self.content = QLabel(
            "No memory data available."
        )



        self.content.setWordWrap(
            True
        )



        self.content.setAlignment(
            Qt.AlignTop
        )



        self.content.setStyleSheet(
            """
            QLabel {

                background-color:#252526;
                border-radius:10px;
                padding:15px;
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
            self.content
        )



        layout.addWidget(
            self.scroll
        )








        self.refresh_button = QPushButton(
            "🔄 Refresh Memory"
        )


        layout.addWidget(
            self.refresh_button
        )





        self.clear_button = QPushButton(
            "🗑 Clear Memory"
        )


        layout.addWidget(
            self.clear_button
        )








        self.setLayout(
            layout
        )









    def update_memory(
        self,
        data
    ):



        if not data:


            self.content.setText(

                "🧠 No memory data available."

            )


            return







        text = ""







        for key, value in data.items():



            if isinstance(
                value,
                dict
            ):



                category = value.get(

                    "category",

                    "general"

                )



                stored_value = value.get(

                    "value",

                    ""

                )



                text += (

                    f"📂 {category.upper()}\n"

                )



                text += (

                    f"🔹 {key}\n"

                )



                text += (

                    f"   ➜ {stored_value}\n"

                )





                if value.get(
                    "created"
                ):


                    text += (

                        f"   🕒 Created: {value.get('created')}\n"

                    )





                if value.get(
                    "updated"
                ):


                    text += (

                        f"   🔄 Updated: {value.get('updated')}\n"

                    )





                text += (

                    "\n----------------------\n\n"

                )





            else:


                text += (

                    f"🔹 {key}: {value}\n\n"

                )







        self.content.setText(
            text
        )