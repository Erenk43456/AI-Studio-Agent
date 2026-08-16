from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QScrollArea
)

from models.model_registry import ModelRegistry

from app.pages.settings.model_section import ModelSection


class SettingsPage(QWidget):

    def __init__(
        self,
        models
    ):

        super().__init__()

        self.models = models
        self.registry = models.registry

        self.build_ui()

    # =========================================================
    # UI
    # =========================================================

    def build_ui(self):

        root = QVBoxLayout()

        # -----------------------------------------------------
        # Title
        # -----------------------------------------------------

        title = QLabel(
            "⚙ Settings"
        )

        title.setStyleSheet(
            """
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: white;
            }
            """
        )

        root.addWidget(
            title
        )

        # -----------------------------------------------------
        # Model sections
        # -----------------------------------------------------

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        content = QWidget()

        layout = QVBoxLayout()

        self.model_sections = {}

        for slot in ModelRegistry.SLOTS:

            section = ModelSection(
                self.registry,
                slot
            )

            section.changed.connect(
                lambda slot=slot:
                self.models.reload_model(slot)
            )

            self.model_sections[slot] = section

            layout.addWidget(
                section
            )

        layout.addStretch()

        content.setLayout(
            layout
        )

        scroll.setWidget(
            content
        )

        root.addWidget(
            scroll
        )

        self.setLayout(
            root
        )