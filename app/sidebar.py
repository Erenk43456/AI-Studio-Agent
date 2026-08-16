from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QListWidget,
    QFrame
)

from PySide6.QtCore import Qt


class Sidebar(QWidget):

    def __init__(self):

        super().__init__()

        self.setObjectName(
            "sidebar"
        )

        self.setFixedWidth(
            230
        )

        layout = QVBoxLayout()

        layout.setContentsMargins(
            12,
            14,
            12,
            14
        )

        layout.setSpacing(
            6
        )

        # =====================================================
        # BRAND
        # =====================================================

        self.brand = QLabel(
            "AI-STUDIO"
        )

        self.brand.setAlignment(
            Qt.AlignLeft
        )

        self.brand.setStyleSheet(
            """
            QLabel {
                color: #f1f3f5;
                font-size: 15px;
                font-weight: 700;
                letter-spacing: 1px;
                padding: 6px 8px;
            }
            """
        )

        layout.addWidget(
            self.brand
        )

        self.brand_subtitle = QLabel(
            "Agent Workspace"
        )

        self.brand_subtitle.setStyleSheet(
            """
            QLabel {
                color: #686f78;
                font-size: 10px;
                padding-left: 8px;
                padding-bottom: 8px;
            }
            """
        )

        layout.addWidget(
            self.brand_subtitle
        )

        # =====================================================
        # NEW CHAT
        # =====================================================

        self.new_chat_button = QPushButton(
            "＋  New Chat"
        )

        self.new_chat_button.setObjectName(
            "newChatButton"
        )

        self.new_chat_button.setMinimumHeight(
            40
        )

        self.new_chat_button.setStyleSheet(
            """
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 9px;
                padding: 9px 12px;
                text-align: left;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #4b8ff7;
            }

            QPushButton:pressed {
                background-color: #326fd1;
            }
            """
        )

        layout.addWidget(
            self.new_chat_button
        )

        # =====================================================
        # CHAT LIST
        # =====================================================

        self.chat_list = QListWidget()

        self.chat_list.setObjectName(
            "chatList"
        )

        self.chat_list.setSpacing(
            2
        )

        self.chat_list.setStyleSheet(
            """
            QListWidget {
                background-color: transparent;
                color: #c9ced4;
                border: none;
                outline: none;
            }

            QListWidget::item {
                background-color: transparent;
                border-radius: 7px;
                padding: 8px 9px;
                margin: 1px 0;
            }

            QListWidget::item:hover {
                background-color: #1d2024;
            }

            QListWidget::item:selected {
                background-color: #24282d;
                color: white;
            }
            """
        )

        layout.addWidget(
            self.chat_list
        )

        # =====================================================
        # NAVIGATION SEPARATOR
        # =====================================================

        separator = QFrame()

        separator.setFrameShape(
            QFrame.HLine
        )

        separator.setStyleSheet(
            """
            QFrame {
                color: #292d32;
                background-color: #292d32;
                max-height: 1px;
            }
            """
        )

        layout.addWidget(
            separator
        )

        layout.addSpacing(
            4
        )

        # =====================================================
        # NAVIGATION BUTTONS
        # =====================================================

        self.chat_button = QPushButton(
            "💬  Chat"
        )

        self.memory_button = QPushButton(
            "🧠  Memory"
        )

        self.history_button = QPushButton(
            "📜  History"
        )

        self.tools_button = QPushButton(
            "🛠  Tools"
        )

        self.formatter_button = QPushButton(
            "🧹  Formatter"
        )

        self.settings_button = QPushButton(
            "⚙  Settings"
        )

        self.navigation_buttons = [
            self.chat_button,
            self.memory_button,
            self.history_button,
            self.tools_button,
            self.formatter_button,
            self.settings_button
        ]

        for button in self.navigation_buttons:

            button.setMinimumHeight(
                38
            )

            button.setStyleSheet(
                """
                QPushButton {
                    background-color: transparent;
                    color: #9ba2aa;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 10px;
                    text-align: left;
                    font-size: 13px;
                }

                QPushButton:hover {
                    background-color: #1d2024;
                    color: #e7e9ec;
                }

                QPushButton:pressed {
                    background-color: #24282d;
                }
                """
            )

            layout.addWidget(
                button
            )

        # =====================================================
        # SPACER
        # =====================================================

        layout.addStretch()

        # =====================================================
        # FOOTER
        # =====================================================

        footer = QLabel(
            "AI-Studio Agent"
        )

        footer.setAlignment(
            Qt.AlignCenter
        )

        footer.setStyleSheet(
            """
            QLabel {
                color: #4f565e;
                font-size: 10px;
                padding: 6px;
            }
            """
        )

        layout.addWidget(
            footer
        )

        # =====================================================
        # INITIAL STATE
        # =====================================================

        self.chat_list.hide()

        self.new_chat_button.hide()

        self.setLayout(
            layout
        )