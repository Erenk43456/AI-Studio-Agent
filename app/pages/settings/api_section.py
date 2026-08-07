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

        # --------------------------------------------------
        # API URL
        # --------------------------------------------------

        self.url_input = QLineEdit()

        self.url_input.setPlaceholderText(
            "API URL"
        )

        self.url_input.setText(
            self.config.get(
                "api_url",
                ""
            )
        )

        # --------------------------------------------------
        # API KEY
        # --------------------------------------------------

        self.key_input = QLineEdit()

        self.key_input.setPlaceholderText(
            "API Key"
        )

        self.key_input.setEchoMode(
            QLineEdit.Password
        )

        self.key_input.setText(
            self.config.get(
                "api_key",
                ""
            )
        )

        # --------------------------------------------------
        # DECISION MODEL
        # --------------------------------------------------

        self.decision_model_input = QLineEdit()

        self.decision_model_input.setPlaceholderText(
            "Decision Model"
        )

        self.decision_model_input.setText(
            self.config.get(
                "decision_model",
                ""
            )
        )

        # --------------------------------------------------
        # PLANNER MODEL
        # --------------------------------------------------

        self.planner_model_input = QLineEdit()

        self.planner_model_input.setPlaceholderText(
            "Planner Model"
        )

        self.planner_model_input.setText(
            self.config.get(
                "planner_model",
                ""
            )
        )

        # --------------------------------------------------
        # CHAT MODEL
        # --------------------------------------------------

        self.chat_model_input = QLineEdit()

        self.chat_model_input.setPlaceholderText(
            "Chat Model"
        )

        self.chat_model_input.setText(
            self.config.get(
                "chat_model",
                ""
            )
        )

        # --------------------------------------------------
        # CODE MODEL
        # --------------------------------------------------

        self.code_model_input = QLineEdit()

        self.code_model_input.setPlaceholderText(
            "Code Model"
        )

        self.code_model_input.setText(
            self.config.get(
                "code_model",
                ""
            )
        )

        # --------------------------------------------------
        # BUTTONS
        # --------------------------------------------------

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

        # --------------------------------------------------
        # LAYOUT
        # --------------------------------------------------

        layout.addWidget(
            title
        )

        layout.addWidget(
            QLabel("API URL")
        )

        layout.addWidget(
            self.url_input
        )

        layout.addWidget(
            QLabel("API Key")
        )

        layout.addWidget(
            self.key_input
        )

        layout.addWidget(
            QLabel("Decision Model")
        )

        layout.addWidget(
            self.decision_model_input
        )

        layout.addWidget(
            QLabel("Planner Model")
        )

        layout.addWidget(
            self.planner_model_input
        )

        layout.addWidget(
            QLabel("Chat Model")
        )

        layout.addWidget(
            self.chat_model_input
        )

        layout.addWidget(
            QLabel("Code Model")
        )

        layout.addWidget(
            self.code_model_input
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

    # ------------------------------------------------------
    # SAVE
    # ------------------------------------------------------

    def save_settings(
        self
    ):

        self.config.update(
            {
                "api_url":
                self.url_input.text(),

                "api_key":
                self.key_input.text(),

                "decision_model":
                self.decision_model_input.text(),

                "planner_model":
                self.planner_model_input.text(),

                "chat_model":
                self.chat_model_input.text(),

                "code_model":
                self.code_model_input.text()
            }
        )

        self.status_label.setText(
            "✅ API settings saved."
        )

    # ------------------------------------------------------
    # TEST
    # ------------------------------------------------------

    def test_connection(
        self
    ):

        try:

            url = self.url_input.text()

            key = self.key_input.text()

            model = (
                self.planner_model_input.text()
                or
                self.chat_model_input.text()
                or
                self.decision_model_input.text()
                or
                self.code_model_input.text()
            )

            if not url:

                self.status_label.setText(
                    "❌ API URL is missing."
                )

                return

            if not model:

                self.status_label.setText(
                    "❌ API model is missing."
                )

                return

            response = requests.post(

                url,

                headers={

                    "Authorization":
                    f"Bearer {key}",

                    "Content-Type":
                    "application/json"

                },

                json={

                    "model":
                    model,

                    "messages": [

                        {

                            "role":
                            "user",

                            "content":
                            "Hello"

                        }

                    ],

                    "temperature":
                    0.3,

                    "max_tokens":
                    10,

                    "stream":
                    False

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