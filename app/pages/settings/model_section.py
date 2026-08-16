from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class ModelSection(QWidget):

    changed = Signal()

    PROVIDERS = {
        "Local": "local",
        "API": "api",
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

        self.group = QGroupBox(
            self.slot.capitalize()
        )

        root = QVBoxLayout()

        form = QFormLayout()

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
            "Model name"
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
        # API key
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
        # Max tokens
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

        # -----------------------------------------------------
        # Buttons
        # -----------------------------------------------------

        buttons = QHBoxLayout()

        self.test_button = QPushButton(
            "Test Connection"
        )

        self.save_button = QPushButton(
            "Save"
        )

        self.reset_button = QPushButton(
            "Reset"
        )

        self.test_button.clicked.connect(
            self.test_connection
        )

        self.save_button.clicked.connect(
            self.save_model
        )

        self.reset_button.clicked.connect(
            self.reset_model
        )

        buttons.addWidget(
            self.test_button
        )

        buttons.addWidget(
            self.save_button
        )

        buttons.addWidget(
            self.reset_button
        )

        root.addLayout(
            buttons
        )

        # -----------------------------------------------------
        # Status
        # -----------------------------------------------------

        self.status_label = QLabel()

        root.addWidget(
            self.status_label
        )

        self.group.setLayout(
            root
        )

        outer = QVBoxLayout()

        outer.addWidget(
            self.group
        )

        self.setLayout(
            outer
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

    # =========================================================
    # PROVIDER
    # =========================================================

    def provider_changed(self):

        self.update_provider_visibility()

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

        self.status_label.setText(
            "✓ Saved"
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

            self.status_label.setText(
                "✓ Reset to defaults"
            )

            self.changed.emit()

        else:

            self.status_label.setText(
                "No defaults available."
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

            self.status_label.setText(
                "✗ Model configuration missing."
            )

            return

        try:

            from models.llm_provider import LLMProvider

            provider = LLMProvider(
                config
            )

            if not provider.check_connection():

                self.status_label.setText(
                    "✗ Connection failed."
                )

                return

            self.status_label.setText(
                "✓ Connection successful."
            )

        except Exception as error:

            self.status_label.setText(
                f"✗ {error}"
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