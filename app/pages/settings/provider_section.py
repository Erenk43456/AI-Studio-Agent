from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QComboBox
)

from PySide6.QtCore import Signal





class ProviderSection(QWidget):


    provider_changed = Signal(str)



    def __init__(
        self,
        config
    ):

        super().__init__()


        self.config = config


        layout = QVBoxLayout()



        title = QLabel(
            "LLM Provider"
        )



        self.combo = QComboBox()



        self.combo.addItems(
            [
                "Local LLM",
                "API LLM"
            ]
        )




        current = self.config.get(
            "llm_provider",
            "local"
        )




        if current == "api":


            self.combo.setCurrentText(
                "API LLM"
            )


        else:


            self.combo.setCurrentText(
                "Local LLM"
            )





        self.combo.currentTextChanged.connect(
            self.save_provider
        )





        layout.addWidget(
            title
        )


        layout.addWidget(
            self.combo
        )



        self.setLayout(
            layout
        )






    def save_provider(
        self,
        value
    ):


        if value == "API LLM":


            provider = "api"



        else:


            provider = "local"




        self.config.set(
            "llm_provider",
            provider
        )



        self.provider_changed.emit(
            provider
        )