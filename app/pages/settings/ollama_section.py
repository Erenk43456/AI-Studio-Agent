from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton
)



class OllamaSection(QWidget):


    def __init__(self, llm):

        super().__init__()


        self.llm = llm


        layout = QVBoxLayout()



        self.status = QLabel(
            "Checking..."
        )


        self.check_button = QPushButton(
            "🔄 Check Ollama"
        )


        self.check_button.clicked.connect(
            self.check_connection
        )



        layout.addWidget(
            self.status
        )


        layout.addWidget(
            self.check_button
        )



        self.setLayout(
            layout
        )



        self.check_connection()






    def check_connection(self):


        if self.llm.check_connection():


            self.status.setText(
                "🟢 Ollama Connected"
            )


        else:


            self.status.setText(
                "🔴 Ollama Offline"
            )