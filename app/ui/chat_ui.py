from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QLabel,
    QFrame
)

from PySide6.QtCore import Qt


class ChatUI:

    @staticmethod
    def create(window):

        # =====================================================
        # CHAT CONTAINER
        # =====================================================

        window.chat_page = QWidget()

        chat_page_layout = QVBoxLayout()

        chat_page_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        chat_page_layout.setSpacing(
            10
        )

        # =====================================================
        # ACTIVE MODEL BAR
        # =====================================================

        window.chat_model_bar = QFrame()

        window.chat_model_bar.setObjectName(
            "chatModelBar"
        )

        model_bar_layout = QHBoxLayout()

        model_bar_layout.setContentsMargins(
            12,
            8,
            12,
            8
        )

        model_bar_layout.setSpacing(
            8
        )

        # =====================================================
        # MODEL SLOT
        # =====================================================

        window.chat_model_slot = QLabel(
            "Chat Model"
        )

        window.chat_model_slot.setStyleSheet(
            """
            QLabel {
                color: #e7e9ec;
                font-size: 12px;
                font-weight: 600;
            }
            """
        )

        model_bar_layout.addWidget(
            window.chat_model_slot
        )

        # =====================================================
        # MODEL NAME
        # =====================================================

        window.chat_model_name = QLabel(
            "Not configured"
        )

        window.chat_model_name.setStyleSheet(
            """
            QLabel {
                color: #c9ced4;
                font-size: 11px;
            }
            """
        )

        model_bar_layout.addWidget(
            window.chat_model_name
        )

        # =====================================================
        # PROVIDER
        # =====================================================

        window.chat_provider = QLabel(
            "Unknown"
        )

        window.chat_provider.setStyleSheet(
            """
            QLabel {
                color: #8f98a3;
                font-size: 11px;
                padding: 4px 8px;
                background-color: #191c20;
                border: 1px solid #30353b;
                border-radius: 6px;
            }
            """
        )

        model_bar_layout.addWidget(
            window.chat_provider
        )

        model_bar_layout.addStretch()

        # =====================================================
        # STATUS
        # =====================================================

        window.chat_model_status = QLabel(
            "● Ready"
        )

        window.chat_model_status.setStyleSheet(
            """
            QLabel {
                color: #8fd694;
                font-size: 11px;
                font-weight: 500;
            }
            """
        )

        model_bar_layout.addWidget(
            window.chat_model_status
        )

        window.chat_model_bar.setLayout(
            model_bar_layout
        )

        chat_page_layout.addWidget(
            window.chat_model_bar
        )

        # =====================================================
        # CHAT AREA
        # =====================================================

        window.chat_widget = QWidget()

        window.chat_layout = QVBoxLayout()

        window.chat_layout.setSpacing(
            12
        )

        window.chat_layout.setContentsMargins(
            10,
            10,
            10,
            10
        )

        window.chat_layout.setAlignment(
            Qt.AlignTop
        )

        window.chat_widget.setLayout(
            window.chat_layout
        )

        window.scroll = QScrollArea()

        window.scroll.setWidgetResizable(
            True
        )

        window.scroll.setWidget(
            window.chat_widget
        )

        chat_page_layout.addWidget(
            window.scroll
        )

        # =====================================================
        # FINAL
        # =====================================================

        window.chat_page.setLayout(
            chat_page_layout
        )

        # =====================================================
        # LOAD ACTIVE MODEL
        # =====================================================

        ChatUI.update_model_info(
            window
        )

    # =========================================================
    # MODEL INFO
    # =========================================================

    @staticmethod
    def update_model_info(window):

        try:

            models = window.container.models

            config = models.registry.get(
                "chat"
            )

            if config is None:

                window.chat_model_name.setText(
                    "Not configured"
                )

                window.chat_provider.setText(
                    "Unknown"
                )

                return

            model_name = (
                config.model
                if config.model
                else "Not configured"
            )

            provider = (
                config.provider
                if config.provider
                else "Unknown"
            )

            provider_text = {
                "local": "Local",
                "api": "API"
            }.get(
                provider,
                provider.upper()
            )

            window.chat_model_name.setText(
                model_name
            )

            window.chat_provider.setText(
                provider_text
            )

        except Exception:

            window.chat_model_name.setText(
                "Unavailable"
            )

            window.chat_provider.setText(
                "Unknown"
            )