from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel
)


from models.llm import LLM

from config.config_manager import ConfigManager

from app.pages.settings.model_section import ModelSection
from app.pages.settings.ollama_section import OllamaSection
from app.pages.settings.config_section import ConfigSection





class SettingsPage(QWidget):


    def __init__(self):

        super().__init__()


        self.config = ConfigManager()


        self.llm = LLM()



        layout = QVBoxLayout()



        title = QLabel(
            "⚙ Settings"
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





        self.model_section = ModelSection(
            self.llm
        )


        self.config_section = ConfigSection(
            self.config
        )


        self.ollama_section = OllamaSection(
            self.llm
        )





        layout.addWidget(
            self.model_section
        )


        layout.addWidget(
            self.config_section
        )


        layout.addWidget(
            self.ollama_section
        )





        self.setLayout(
            layout
        )