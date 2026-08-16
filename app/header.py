from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel
)

from PySide6.QtCore import Qt


class Header(QWidget):

    def __init__(self):

        super().__init__()

        self.setObjectName(
            "header"
        )

        layout = QHBoxLayout()

        layout.setContentsMargins(
            18,
            10,
            18,
            10
        )

        layout.setSpacing(
            12
        )

        # =====================================================
        # BRAND
        # =====================================================

        brand_layout = QVBoxLayout()

        brand_layout.setSpacing(
            2
        )

        self.title = QLabel(
            "AI-Studio Agent"
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

        self.subtitle = QLabel(
            "Local AI Workspace"
        )

        self.subtitle.setStyleSheet(
            """
            QLabel {
                color: #7f8791;
                font-size: 11px;
            }
            """
        )

        brand_layout.addWidget(
            self.title
        )

        brand_layout.addWidget(
            self.subtitle
        )

        layout.addLayout(
            brand_layout
        )

        layout.addStretch()

        # =====================================================
        # MODEL INFO
        # =====================================================

        self.model = QLabel(
            "Chat Model"
        )

        self.model.setAlignment(
            Qt.AlignRight |
            Qt.AlignVCenter
        )

        self.model.setStyleSheet(
            """
            QLabel {
                color: #c9ced4;
                font-size: 12px;
                font-weight: 500;
                padding: 6px 10px;
                background-color: #191c20;
                border: 1px solid #30353b;
                border-radius: 7px;
            }
            """
        )

        layout.addWidget(
            self.model
        )

        # =====================================================
        # PROVIDER
        # =====================================================

        self.provider = QLabel(
            "● Local LLM"
        )

        self.provider.setAlignment(
            Qt.AlignCenter
        )

        self.provider.setStyleSheet(
            """
            QLabel {
                color: #8fd694;
                font-size: 11px;
                padding: 6px 10px;
                background-color: #17201a;
                border: 1px solid #263a2b;
                border-radius: 7px;
            }
            """
        )

        layout.addWidget(
            self.provider
        )

        self.setLayout(
            layout
        )