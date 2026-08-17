from PySide6.QtCore import Qt, Signal

from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from models.model_registry import ModelRegistry

from app.pages.settings.model_section import ModelSection


class SettingsPage(QWidget):

    model_updated = Signal(str)

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
        models
    ):

        super().__init__()

        self.models = models
        self.registry = models.registry

        self.model_sections = {}

        self.build_ui()

    # =========================================================
    # UI
    # =========================================================

    def build_ui(self):

        root = QVBoxLayout()

        root.setContentsMargins(
            18,
            16,
            18,
            16
        )

        root.setSpacing(
            14
        )

        # =====================================================
        # HEADER
        # =====================================================

        title = QLabel(
            "⚙  Settings"
        )

        title.setStyleSheet(
            """
            QLabel {
                color: #f1f3f5;
                font-size: 22px;
                font-weight: 600;
            }
            """
        )

        root.addWidget(
            title
        )

        subtitle = QLabel(
            "Configure the AI models used by AI-Studio Agent."
        )

        subtitle.setStyleSheet(
            """
            QLabel {
                color: #737b85;
                font-size: 12px;
            }
            """
        )

        root.addWidget(
            subtitle
        )

        # =====================================================
        # MODEL STATUS
        # =====================================================

        status_title = QLabel(
            "MODEL STATUS"
        )

        status_title.setStyleSheet(
            """
            QLabel {
                color: #686f78;
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 1px;
                padding-top: 8px;
            }
            """
        )

        root.addWidget(
            status_title
        )

        status_frame = QFrame()

        status_frame.setStyleSheet(
            """
            QFrame {
                background-color: #151719;
                border: 1px solid #292d32;
                border-radius: 10px;
            }
            """
        )

        status_layout = QHBoxLayout()

        status_layout.setContentsMargins(
            10,
            10,
            10,
            10
        )

        status_layout.setSpacing(
            8
        )

        self.status_labels = {}

        for slot in ModelRegistry.SLOTS:

            card = QFrame()

            card.setStyleSheet(
                """
                QFrame {
                    background-color: #191c20;
                    border: 1px solid #30353b;
                    border-radius: 8px;
                }
                """
            )

            card_layout = QVBoxLayout()

            card_layout.setContentsMargins(
                10,
                8,
                10,
                8
            )

            card_layout.setSpacing(
                3
            )

            name = QLabel(
                f"{self.SLOT_ICONS.get(slot, '🤖')}  "
                f"{self.SLOT_NAMES.get(slot, slot.capitalize())}"
            )

            name.setStyleSheet(
                """
                QLabel {
                    color: #c9ced4;
                    font-size: 11px;
                    font-weight: 600;
                    border: none;
                    background: transparent;
                }
                """
            )

            status = QLabel(
                "● Checking"
            )

            status.setStyleSheet(
                """
                QLabel {
                    color: #737b85;
                    font-size: 10px;
                    border: none;
                    background: transparent;
                }
                """
            )

            card_layout.addWidget(
                name
            )

            card_layout.addWidget(
                status
            )

            card.setLayout(
                card_layout
            )

            status_layout.addWidget(
                card
            )

            self.status_labels[slot] = status

        status_frame.setLayout(
            status_layout
        )

        root.addWidget(
            status_frame
        )

        # =====================================================
        # MODEL SELECTOR
        # =====================================================

        selector_row = QHBoxLayout()

        selector_row.setContentsMargins(
            0,
            6,
            0,
            0
        )

        selector_label = QLabel(
            "Model"
        )

        selector_label.setStyleSheet(
            """
            QLabel {
                color: #9ba2aa;
                font-size: 12px;
                font-weight: 500;
            }
            """
        )

        selector_row.addWidget(
            selector_label
        )

        self.model_selector = QComboBox()

        self.model_selector.setMinimumHeight(
            38
        )

        self.model_selector.setMinimumWidth(
            260
        )

        for slot in ModelRegistry.SLOTS:

            self.model_selector.addItem(
                f"{self.SLOT_ICONS.get(slot, '🤖')}  "
                f"{self.SLOT_NAMES.get(slot, slot.capitalize())}",
                slot
            )

        self.model_selector.currentIndexChanged.connect(
            self.switch_model
        )

        selector_row.addWidget(
            self.model_selector
        )

        selector_row.addStretch()

        root.addLayout(
            selector_row
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
        # MODEL CONTENT
        # =====================================================

        self.scroll = QScrollArea()

        self.scroll.setWidgetResizable(
            True
        )

        self.scroll.setFrameShape(
            QFrame.NoFrame
        )

        content = QWidget()

        self.content_layout = QVBoxLayout()

        self.content_layout.setContentsMargins(
            4,
            4,
            4,
            4
        )

        self.content_layout.setSpacing(
            0
        )

        # Create all sections once.
        # Only one is visible at a time.

        for slot in ModelRegistry.SLOTS:

            section = ModelSection(
                self.registry,
                slot
            )

            section.changed.connect(
                lambda slot=slot:
                self.model_changed(slot)
            )

            self.model_sections[slot] = section

            self.content_layout.addWidget(
                section
            )

            section.setVisible(
                False
            )

        self.content_layout.addStretch()

        content.setLayout(
            self.content_layout
        )

        self.scroll.setWidget(
            content
        )

        root.addWidget(
            self.scroll
        )

        self.setLayout(
            root
        )

        # =====================================================
        # INITIAL MODEL
        # =====================================================

        if ModelRegistry.SLOTS:

            self.model_selector.setCurrentIndex(
                0
            )

            self.switch_model(
                0
            )

        self.refresh_status()

    # =========================================================
    # SWITCH MODEL
    # =========================================================

    def switch_model(
        self,
        index
    ):

        slot = self.model_selector.itemData(
            index
        )

        if not slot:

            return

        for current_slot, section in self.model_sections.items():

            section.setVisible(
                current_slot == slot
            )

        self.refresh_status()

    # =========================================================
    # MODEL CHANGED
    # =========================================================

    def model_changed(
        self,
        slot
    ):

        section = self.model_sections.get(
            slot
        )

        if section:

            section.load_model()

        self.refresh_status()

        self.model_updated.emit(
            slot
        )

    # =========================================================
    # STATUS
    # =========================================================

    def refresh_status(self):

        for slot in ModelRegistry.SLOTS:

            label = self.status_labels.get(
                slot
            )

            if label is None:

                continue

            config = self.registry.get(
                slot
            )

            if config is None:

                label.setText(
                    "● Not Configured"
                )

                label.setStyleSheet(
                    """
                    QLabel {
                        color: #f0ad4e;
                        font-size: 10px;
                        border: none;
                        background: transparent;
                    }
                    """
                )

                continue

            if not config.enabled:

                label.setText(
                    "● Disabled"
                )

                label.setStyleSheet(
                    """
                    QLabel {
                        color: #737b85;
                        font-size: 10px;
                        border: none;
                        background: transparent;
                    }
                    """
                )

                continue

            if not config.model:

                label.setText(
                    "● Not Configured"
                )

                label.setStyleSheet(
                    """
                    QLabel {
                        color: #f0ad4e;
                        font-size: 10px;
                        border: none;
                        background: transparent;
                    }
                    """
                )

                continue

            provider = (
                "API"
                if config.provider == "api"
                else "Local"
            )

            label.setText(
                f"● Active · {provider}"
            )

            label.setStyleSheet(
                """
                QLabel {
                    color: #8fd694;
                    font-size: 10px;
                    border: none;
                    background: transparent;
                }
                """
            )

    # =========================================================
    # REFRESH
    # =========================================================

    def refresh(self):

        for slot, section in self.model_sections.items():

            section.load_model()

        self.refresh_status()