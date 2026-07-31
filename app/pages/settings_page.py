from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel
)


from config.config_manager import ConfigManager


from app.pages.settings.model_section import ModelSection
from app.pages.settings.ollama_section import OllamaSection
from app.pages.settings.config_section import ConfigSection
from app.pages.settings.provider_section import ProviderSection
from app.pages.settings.api_section import APISection





class SettingsPage(QWidget):


    def __init__(
        self,
        llm
    ):


        super().__init__()



        self.config = ConfigManager()


        self.llm = llm







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









        self.provider_section = ProviderSection(
            self.config
        )



        self.api_section = APISection(
            self.config
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








        self.provider_section.provider_changed.connect(

            self.change_provider

        )









        layout.addWidget(
            self.provider_section
        )


        layout.addWidget(
            self.api_section
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








        self.change_provider(

            self.config.get(

                "llm_provider",

                "local"

            )

        )









    def change_provider(

        self,

        provider

    ):



        if provider == "api":



            self.api_section.show()

            self.model_section.hide()

            self.ollama_section.hide()



        else:



            self.api_section.hide()

            self.model_section.show()

            self.ollama_section.show()