import json
import os


from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton
)


from models.llm import LLM




class SettingsPage(QWidget):


    def __init__(self):

        super().__init__()


        self.config_path = "config/settings.json"


        self.llm = LLM()



        layout = QVBoxLayout()



        #
        # Title
        #

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




        #
        # Model
        #

        model_label = QLabel(
            "LLM Model"
        )


        self.model_box = QComboBox()


        self.refresh_models()



        layout.addWidget(
            model_label
        )


        layout.addWidget(
            self.model_box
        )




        #
        # Temperature
        #

        temp_label = QLabel(
            "Temperature"
        )


        self.temperature_box = QDoubleSpinBox()


        self.temperature_box.setRange(
            0.0,
            1.0
        )


        self.temperature_box.setSingleStep(
            0.1
        )


        layout.addWidget(
            temp_label
        )


        layout.addWidget(
            self.temperature_box
        )





        #
        # Tokens
        #

        token_label = QLabel(
            "Max Tokens"
        )


        self.token_box = QSpinBox()


        self.token_box.setRange(
            50,
            2000
        )


        layout.addWidget(
            token_label
        )


        layout.addWidget(
            self.token_box
        )





        #
        # Ollama Status
        #

        self.ollama_status = QLabel(
            "Checking..."
        )


        layout.addWidget(
            self.ollama_status
        )




        self.check_button = QPushButton(
            "🔄 Check Ollama"
        )


        self.check_button.clicked.connect(
            self.check_ollama
        )


        layout.addWidget(
            self.check_button
        )





        #
        # Refresh Models
        #

        self.refresh_button = QPushButton(
            "Refresh Models"
        )


        self.refresh_button.clicked.connect(
            self.refresh_models
        )


        layout.addWidget(
            self.refresh_button
        )






        #
        # Save
        #

        self.save_button = QPushButton(
            "Save Settings"
        )


        self.save_button.clicked.connect(
            self.save_settings
        )


        layout.addWidget(
            self.save_button
        )



        self.save_status = QLabel(
            ""
        )


        layout.addWidget(
            self.save_status
        )



        self.setLayout(
            layout
        )



        self.load_settings()

        self.check_ollama()





    def refresh_models(self):


        models = self.llm.get_models()



        current = self.model_box.currentText()



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



        if current:

            index = self.model_box.findText(
                current
            )


            if index >= 0:

                self.model_box.setCurrentIndex(
                    index
                )






    def load_settings(self):


        if os.path.exists(
            self.config_path
        ):


            with open(
                self.config_path,
                "r",
                encoding="utf-8"
            ) as file:


                data = json.load(
                    file
                )



            model = data.get(
                "model"
            )



            if model:

                index = self.model_box.findText(
                    model
                )


                if index >= 0:

                    self.model_box.setCurrentIndex(
                        index
                    )



            self.temperature_box.setValue(
                data.get(
                    "temperature",
                    0.3
                )
            )


            self.token_box.setValue(
                data.get(
                    "num_predict",
                    150
                )
            )






    def save_settings(self):


        data = {


            "model":
            self.model_box.currentText(),


            "temperature":
            self.temperature_box.value(),


            "num_predict":
            self.token_box.value(),


            "ollama_url":
            "http://localhost:11434/api/generate"

        }




        os.makedirs(
            "config",
            exist_ok=True
        )



        with open(
            self.config_path,
            "w",
            encoding="utf-8"
        ) as file:


            json.dump(
                data,
                file,
                indent=4
            )



        self.save_status.setText(
            "✅ Settings saved"
        )





    def check_ollama(self):


        if self.llm.check_connection():


            self.ollama_status.setText(
                "🟢 Ollama Connected"
            )


        else:


            self.ollama_status.setText(
                "🔴 Ollama Offline"
            )