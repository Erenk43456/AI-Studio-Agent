from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton
)


import requests


from app.core.logger import AppLogger





class APISection(QWidget):


    def __init__(
        self,
        config
    ):

        super().__init__()


        self.config = config

        self.logger = AppLogger()



        layout = QVBoxLayout()





        title = QLabel(
            "API Settings"
        )





        self.url_input = QLineEdit()


        self.url_input.setPlaceholderText(
            "API URL"
        )





        self.model_input = QLineEdit()


        self.model_input.setPlaceholderText(
            "API Model"
        )





        self.key_input = QLineEdit()


        self.key_input.setPlaceholderText(
            "API Key"
        )


        self.key_input.setEchoMode(
            QLineEdit.Password
        )







        self.url_input.setText(

            self.config.get(
                "api_url",
                ""
            )

        )



        self.model_input.setText(

            self.config.get(
                "api_model",
                ""
            )

        )



        self.key_input.setText(

            self.config.get(
                "api_key",
                ""
            )

        )







        save_button = QPushButton(
            "Save API Settings"
        )


        save_button.clicked.connect(
            self.save_settings
        )






        test_button = QPushButton(
            "Test API Connection"
        )


        test_button.clicked.connect(
            self.test_connection
        )







        self.status_label = QLabel(
            ""
        )







        layout.addWidget(
            title
        )


        layout.addWidget(
            self.url_input
        )


        layout.addWidget(
            self.model_input
        )


        layout.addWidget(
            self.key_input
        )


        layout.addWidget(
            save_button
        )


        layout.addWidget(
            test_button
        )


        layout.addWidget(
            self.status_label
        )





        self.setLayout(
            layout
        )








    def save_settings(
        self
    ):



        self.config.set(
            "api_url",
            self.url_input.text()
        )



        self.config.set(
            "api_model",
            self.model_input.text()
        )



        self.config.set(
            "api_key",
            self.key_input.text()
        )



        self.config.save()



        self.status_label.setText(
            "✅ API settings saved."
        )








    def test_connection(
        self
    ):


        try:


            url = self.url_input.text()


            model = self.model_input.text()


            key = self.key_input.text()





            response = requests.post(


                url,


                headers={


                    "Authorization":
                    f"Bearer {key}",


                    "Content-Type":
                    "application/json"

                },


                json={


                    "model": model,


                    "messages":[

                        {

                            "role":"user",

                            "content":"Hello"

                        }

                    ],

                    "max_tokens":10

                },


                timeout=30

            )





            response.raise_for_status()





            self.status_label.setText(

                "✅ API connection successful."

            )



        except Exception as error:


            self.logger.error(

                f"API test error: {error}"

            )


            self.status_label.setText(

                f"❌ API Error: {error}"

            )