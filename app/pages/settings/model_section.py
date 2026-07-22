from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QPushButton
)



class ModelSection(QWidget):


    def __init__(self, llm):

        super().__init__()


        self.llm = llm


        layout = QVBoxLayout()



        label = QLabel(
            "LLM Model"
        )


        self.model_box = QComboBox()


        self.refresh_button = QPushButton(
            "Refresh Models"
        )


        self.refresh_button.clicked.connect(
            self.refresh_models
        )



        layout.addWidget(
            label
        )


        layout.addWidget(
            self.model_box
        )


        layout.addWidget(
            self.refresh_button
        )



        self.setLayout(
            layout
        )



        self.refresh_models()






    def refresh_models(self):


        models = self.llm.get_models()


        self.model_box.clear()



        if models:


            self.model_box.addItems(
                models
            )


        else:


            self.model_box.addItems(
                [
                    "qwen2.5:3b",
                    "qwen2.5:1.5b"
                ]
            )





    def get_model(self):


        return self.model_box.currentText()