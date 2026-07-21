from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class MemoryPage(QWidget):

    def __init__(self):

        super().__init__()


        layout = QVBoxLayout()


        self.label = QLabel(
            "🧠 Hafıza\n\nHenüz veri yok."
        )


        self.label.setStyleSheet(
            """
            QLabel {
                font-size:16px;
                color:white;
            }
            """
        )


        layout.addWidget(
            self.label
        )


        self.setLayout(
            layout
        )



    def update_memory(
        self,
        data
    ):

        text = "🧠 Hafıza\n\n"


        for key,value in data.items():

            text += f"{key}: {value}\n"



        self.label.setText(
            text
        )