from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QSizePolicy
)

from PySide6.QtCore import Qt


from app.header import Header
from app.sidebar import Sidebar

from app.ui.styles import AppStyles
from app.ui.chat_ui import ChatUI
from app.ui.page_manager import PageManager


class UIBuilder:

    # =========================================================
    # WINDOW
    # =========================================================

    @staticmethod
    def setup_window(window):

        window.setWindowTitle(
            "AI-Studio-Agent"
        )

        window.resize(
            1200,
            760
        )

        window.setMinimumSize(
            900,
            600
        )

        window.setStyleSheet(
            AppStyles.MAIN_STYLE
        )

    # =========================================================
    # BUILD
    # =========================================================

    @staticmethod
    def build(window):

        main_layout = QVBoxLayout()

        main_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        main_layout.setSpacing(
            0
        )

        # =====================================================
        # HEADER
        # =====================================================

        window.header = Header()

        main_layout.addWidget(
            window.header
        )

        # =====================================================
        # CONTENT
        # =====================================================

        content_layout = QHBoxLayout()

        content_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        content_layout.setSpacing(
            0
        )

        # =====================================================
        # SIDEBAR
        # =====================================================

        window.sidebar = Sidebar()

        content_layout.addWidget(
            window.sidebar
        )

        # =====================================================
        # MAIN AREA
        # =====================================================

        main_area = QWidget()

        main_area.setObjectName(
            "mainArea"
        )

        main_area_layout = QVBoxLayout()

        main_area_layout.setContentsMargins(
            18,
            14,
            18,
            14
        )

        main_area_layout.setSpacing(
            10
        )

        # =====================================================
        # CHAT / PAGES
        # =====================================================

        ChatUI.create(
            window
        )

        PageManager.create(
            window
        )

        main_area_layout.addWidget(
            window.pages
        )

        # =====================================================
        # STATUS
        # =====================================================

        status_row = QHBoxLayout()

        status_row.setContentsMargins(
            4,
            0,
            4,
            0
        )

        status_row.setSpacing(
            6
        )

        window.status = QLabel(
            "Ready"
        )

        window.status.setObjectName(
            "statusLabel"
        )

        window.status.setAlignment(
            Qt.AlignLeft |
            Qt.AlignVCenter
        )

        status_row.addWidget(
            window.status
        )

        status_row.addStretch()

        main_area_layout.addLayout(
            status_row
        )

        # =====================================================
        # MESSAGE COMPOSER
        # =====================================================

        composer = QFrame()

        composer.setObjectName(
            "composer"
        )

        composer_layout = QHBoxLayout()

        composer_layout.setContentsMargins(
            6,
            6,
            6,
            6
        )

        composer_layout.setSpacing(
            4
        )

        # =====================================================
        # INPUT
        # =====================================================

        window.input = QLineEdit()

        window.input.setObjectName(
            "messageInput"
        )

        window.input.setPlaceholderText(
            "Ask AI-Studio anything..."
        )

        window.input.setMinimumHeight(
            42
        )

        window.input.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        composer_layout.addWidget(
            window.input
        )

        # =====================================================
        # SEND
        # =====================================================

        window.button = QPushButton(
            "Send  ➤"
        )

        window.button.setObjectName(
            "sendButton"
        )

        window.button.setMinimumHeight(
            42
        )

        window.button.setMinimumWidth(
            95
        )

        composer_layout.addWidget(
            window.button
        )

        composer.setLayout(
            composer_layout
        )

        main_area_layout.addWidget(
            composer
        )

        # =====================================================
        # FINALIZE MAIN AREA
        # =====================================================

        main_area.setLayout(
            main_area_layout
        )

        content_layout.addWidget(
            main_area
        )

        # =====================================================
        # FINAL WINDOW LAYOUT
        # =====================================================

        main_layout.addLayout(
            content_layout
        )

        window.setLayout(
            main_layout
        )