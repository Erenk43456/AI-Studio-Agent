from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QFrame,
)


class ModelSection(QWidget):

    changed = Signal()

    PROVIDERS = {
        "Local": "local",
        "API": "api",
    }

    SLOT_NAMES = {
        "chat": "Chat Model",
        "code": "Code Model",
        "planner": "Planner Model",
        "decision": "Decision Model",
    }

    SLOT_ICONS = {
        "chat": "💬",
        "code": "💻",
        "planner": "🧠",
        "decision": "⚖",
    }

    def __init__(
        self,
        registry,
        slot,
        parent=None
    ):

        super().__init__(parent)

        self.registry = registry
        self.slot = slot

        self.build_ui()
        self.load_model()

    # =========================================================
    # UI
    # =========================================================

    def build_ui(self):

        root = QVBoxLayout()

        root.setContentsMargins(
            0,
            0,
            0,
            0
        )

        root.setSpacing(
            14
        )

        # =====================================================
        # HEADER
        # =====================================================

        header = QHBoxLayout()

        header.setSpacing(
            10
        )

        icon = self.SLOT_ICONS.get(
            self.slot,
            "🤖"
        )

        name = self.SLOT_NAMES.get(
            self.slot,
            self.slot.capitalize()
        )

        self.title = QLabel(
            f"{icon}  {name}"
        )

        self.title.setStyleSheet(
            """
            QLabel {
                color: #f1f3f5;
                font-size: 18px;
                font-weight: 600;
            }
            """
        )

        header.addWidget(
            self.title
        )

        header.addStretch()

        self.status_label = QLabel(
            "● Active"
        )

        self.status_label.setStyleSheet(
            """
            QLabel {
                color: #8fd694;
                background-color: #17201a;
                border: 1px solid #263a2b;
                border-radius: 7px;
                padding: 5px 9px;
                font-size: 11px;
                font-weight: 600;
            }
            """
        )

        header.addWidget(
            self.status_label
        )

        root.addLayout(
            header
        )

        # =====================================================
        # DESCRIPTION
        # =====================================================

        description = QLabel(
            "Configure the model used for this agent role."
        )

        description.setStyleSheet(
            """
            QLabel {
                color: #737b85;
                font-size: 12px;
            }
            """
        )

        root.addWidget(
            description
        )

        # =====================================================
        # DIVIDER
        # =====================================================

        divider = QFrame()

        divider.setFrameShape(
            QFrame.HLine
        )

        divider.setStyleSheet(
            """
            QFrame {
                color: #292d32;
                background-color: #292d32;
                max-height: 1px;
            }
            """
        )

        root.addWidget(
            divider
        )

        # =====================================================
        # FORM
        # =====================================================

        form = QFormLayout()

        form.setHorizontalSpacing(
            20
        )

        form.setVerticalSpacing(
            12
        )

        # -----------------------------------------------------
        # Provider
        # -----------------------------------------------------

        self.provider_box = QComboBox()

        for label, value in self.PROVIDERS.items():

            self.provider_box.addItem(
                label,
                value
            )

        self.provider_box.currentIndexChanged.connect(
            self.provider_changed
        )

        form.addRow(
            "Provider",
            self.provider_box
        )

        # -----------------------------------------------------
        # Model
        # -----------------------------------------------------

        self.model_input = QLineEdit()

        self.model_input.setPlaceholderText(
            "Model identifier"
        )

        form.addRow(
            "Model",
            self.model_input
        )

        # -----------------------------------------------------
        # Endpoint
        # -----------------------------------------------------

        self.endpoint_input = QLineEdit()

        self.endpoint_input.setPlaceholderText(
            "http://localhost:11434"
        )

        form.addRow(
            "Endpoint",
            self.endpoint_input
        )

        # -----------------------------------------------------
        # API Key
        # -----------------------------------------------------

        self.api_key_input = QLineEdit()

        self.api_key_input.setEchoMode(
            QLineEdit.Password
        )

        self.api_key_input.setPlaceholderText(
            "API key"
        )

        form.addRow(
            "API Key",
            self.api_key_input
        )

        # -----------------------------------------------------
        # Temperature
        # -----------------------------------------------------

        self.temperature_input = QDoubleSpinBox()

        self.temperature_input.setRange(
            0.0,
            2.0
        )

        self.temperature_input.setSingleStep(
            0.05
        )

        self.temperature_input.setDecimals(
            2
        )

        form.addRow(
            "Temperature",
            self.temperature_input
        )

        # -----------------------------------------------------
        # Max Tokens
        # -----------------------------------------------------

        self.max_tokens_input = QSpinBox()

        self.max_tokens_input.setRange(
            1,
            1_000_000
        )

        form.addRow(
            "Max Tokens",
            self.max_tokens_input
        )

        # -----------------------------------------------------
        # Timeout
        # -----------------------------------------------------

        self.timeout_input = QSpinBox()

        self.timeout_input.setRange(
            1,
            3600
        )

        form.addRow(
            "Timeout",
            self.timeout_input
        )

        root.addLayout(
            form
        )

        # =====================================================
        # ACTIONS
        # =====================================================

        actions = QHBoxLayout()

        actions.setSpacing(
            8
        )

        self.test_button = QPushButton(
            "Test Connection"
        )

        self.reset_button = QPushButton(
            "Reset"
        )

        self.save_button = QPushButton(
            "Save Changes"
        )

        self.save_button.setObjectName(
            "sendButton"
        )

        self.test_button.clicked.connect(
            self.test_connection
        )

        self.reset_button.clicked.connect(
            self.reset_model
        )

        self.save_button.clicked.connect(
            self.save_model
        )

        actions.addWidget(
            self.test_button
        )

        actions.addWidget(
            self.reset_button
        )

        actions.addStretch()

        actions.addWidget(
            self.save_button
        )

        root.addLayout(
            actions
        )

        self.setLayout(
            root
        )

    # =========================================================
    # LOAD
    # =========================================================

    def load_model(self):

        config = self.registry.get(
            self.slot
        )

        if config is None:

            return

        provider_text = "API"

        if config.provider == "local":

            provider_text = "Local"

        self.provider_box.setCurrentText(
            provider_text
        )

        self.model_input.setText(
            config.model
        )

        self.endpoint_input.setText(
            config.endpoint
        )

        self.api_key_input.setText(
            config.api_key
        )

        self.temperature_input.setValue(
            config.temperature
        )

        self.max_tokens_input.setValue(
            config.max_tokens
        )

        self.timeout_input.setValue(
            config.timeout
        )

        self.update_provider_visibility()

        self.update_status()

    # =========================================================
    # PROVIDER
    # =========================================================

    def provider_changed(self):

        self.update_provider_visibility()

        self.update_status()

    def update_provider_visibility(self):

        provider = self.provider_box.currentData()

        is_api = (
            provider == "api"
        )

        self.api_key_input.setVisible(
            is_api
        )

        api_label = self._find_form_label(
            self.api_key_input
        )

        if api_label:

            api_label.setVisible(
                is_api
            )

    # =========================================================
    # STATUS
    # =========================================================

    def update_status(
        self,
        text=None,
        success=True
    ):

        if text is not None:

            if success:

                self.status_label.setText(
                    f"● {text}"
                )

                self.status_label.setStyleSheet(
                    """
                    QLabel {
                        color: #8fd694;
                        background-color: #17201a;
                        border: 1px solid #263a2b;
                        border-radius: 7px;
                        padding: 5px 9px;
                        font-size: 11px;
                        font-weight: 600;
                    }
                    """
                )

            else:

                self.status_label.setText(
                    f"● {text}"
                )

                self.status_label.setStyleSheet(
                    """
                    QLabel {
                        color: #f28b82;
                        background-color: #241716;
                        border: 1px solid #402523;
                        border-radius: 7px;
                        padding: 5px 9px;
                        font-size: 11px;
                        font-weight: 600;
                    }
                    """
                )

            return

        config = self.registry.get(
            self.slot
        )

        if config is None:

            self.status_label.setText(
                "● Not Configured"
            )

            return

        if not config.enabled:

            self.status_label.setText(
                "● Disabled"
            )

            return

        if not config.model:

            self.status_label.setText(
                "● Not Configured"
            )

            return

        self.status_label.setText(
            "● Active"
        )

    # =========================================================
    # SAVE
    # =========================================================

    def save_model(self):

        provider_text = (
            self.provider_box.currentText()
        )

        provider = self.PROVIDERS.get(
            provider_text,
            "local"
        )

        api_key = (
            self.api_key_input.text()
            if provider == "api"
            else ""
        )

        self.registry.update(
            self.slot,
            provider=provider,
            model=self.model_input.text().strip(),
            endpoint=self.endpoint_input.text().strip(),
            api_key=api_key,
            temperature=self.temperature_input.value(),
            max_tokens=self.max_tokens_input.value(),
            timeout=self.timeout_input.value()
        )

        self.update_status(
            "Saved",
            True
        )

        self.changed.emit()

    # =========================================================
    # RESET
    # =========================================================

    def reset_model(self):

        if self.registry.reset(
            self.slot
        ):

            self.load_model()

            self.update_status(
                "Reset",
                True
            )

            self.changed.emit()

        else:

            self.update_status(
                "No Defaults",
                False
            )

    # =========================================================
    # TEST
    # =========================================================

    def test_connection(self):

        self.save_model()

        config = self.registry.get(
            self.slot
        )

        if config is None:

            self.update_status(
                "Configuration Error",
                False
            )

            return

        self.test_button.setEnabled(
            False
        )

        self.update_status(
            "Testing...",
            True
        )

        try:

            from models.llm_provider import LLMProvider

            provider = LLMProvider(
                config
            )

            if not provider.check_connection():

                self.update_status(
                    "Connection Failed",
                    False
                )

                return

            self.update_status(
                "Connected",
                True
            )

        except Exception as error:

            self.update_status(
                "Connection Failed",
                False
            )

        finally:

            self.test_button.setEnabled(
                True
            )

    # =========================================================
    # FORM LABEL HELPER
    # =========================================================

    def _find_form_label(
        self,
        widget
    ):

        parent = widget.parentWidget()

        if parent is None:

            return None

        form = parent.layout()

        if not isinstance(
            form,
            QFormLayout
        ):

            return None

        for row in range(
            form.rowCount()
        ):

            field = form.itemAt(
                row,
                QFormLayout.FieldRole
            )

            label = form.itemAt(
                row,
                QFormLayout.LabelRole
            )

            if (
                field
                and
                field.widget() is widget
            ):

                if label:

                    return label.widget()

        return None