from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QListWidget,
    QFrame,
)

from PySide6.QtCore import Qt


class Sidebar(QWidget):

    def __init__(self):

        super().__init__()

        self.setFixedWidth(230)

        self.setObjectName("sidebar")

        self.setStyleSheet(
            """
            QWidget#sidebar {
                background-color: #111318;
                border-right: 1px solid #232832;
            }

            QLabel#appTitle {
                color: #f4f4f5;
                font-size: 15px;
                font-weight: 700;
                padding: 8px 4px;
            }

            QLabel#sectionLabel {
                color: #717784;
                font-size: 11px;
                font-weight: 700;
                padding: 8px 10px 4px 10px;
            }

            QPushButton {
                background-color: transparent;
                color: #b8bdc7;
                border: none;
                border-radius: 9px;
                padding: 10px 12px;
                text-align: left;
                font-size: 13px;
            }

            QPushButton:hover {
                background-color: #1c2027;
                color: #f4f4f5;
            }

            QPushButton:pressed {
                background-color: #242933;
            }

            QPushButton:checked {
                background-color: #202633;
                color: #ffffff;
            }

            QPushButton#newChatButton {
                background-color: #2563eb;
                color: white;
                font-weight: 700;
                border-radius: 9px;
                padding: 11px 12px;
            }

            QPushButton#newChatButton:hover {
                background-color: #3b82f6;
            }

            QListWidget {
                background-color: transparent;
                color: #b8bdc7;
                border: none;
                outline: none;
                padding: 2px 0;
            }

            QListWidget::item {
                padding: 9px 10px;
                margin: 2px 0;
                border-radius: 8px;
            }

            QListWidget::item:hover {
                background-color: #1c2027;
                color: #ffffff;
            }

            QListWidget::item:selected {
                background-color: #242a35;
                color: #ffffff;
            }

            QFrame#separator {
                background-color: #232832;
                min-height: 1px;
                max-height: 1px;
                border: none;
            }
            """
        )

        layout = QVBoxLayout()

        layout.setContentsMargins(
            12,
            14,
            12,
            12
        )

        layout.setSpacing(5)

        # =====================================================
        # HEADER
        # =====================================================

        title = QLabel(
            "AI-Studio"
        )

        title.setObjectName(
            "appTitle"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            title
        )

        layout.addSpacing(
            8
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

        layout.addWidget(
            self.new_chat_button
        )

        # =====================================================
        # CHAT LIST
        # =====================================================

        self.chat_list = QListWidget()

        self.chat_list.setMinimumHeight(
            120
        )

        # Chat list initially hidden.
        self.chat_list.hide()

        self.new_chat_button.hide()

        layout.addWidget(
            self.chat_list
        )

        # =====================================================
        # SEPARATOR
        # =====================================================

        separator = QFrame()

        separator.setObjectName(
            "separator"
        )

        layout.addWidget(
            separator
        )

        layout.addSpacing(
            6
        )

        # =====================================================
        # NAVIGATION
        # =====================================================

        self.chat_button = QPushButton(
            "💬   Chat"
        )

        self.memory_button = QPushButton(
            "🧠   Memory"
        )

        self.history_button = QPushButton(
            "📜   History"
        )

        self.tools_button = QPushButton(
            "🛠   Tools"
        )

        self.formatter_button = QPushButton(
            "🧹   Formatter"
        )

        self.settings_button = QPushButton(
            "⚙   Settings"
        )

        layout.addWidget(
            self.chat_button
        )

        layout.addWidget(
            self.memory_button
        )

        layout.addWidget(
            self.history_button
        )

        layout.addWidget(
            self.tools_button
        )

        layout.addWidget(
            self.formatter_button
        )

        layout.addWidget(
            self.settings_button
        )

        layout.addStretch()

        self.setLayout(
            layout
        )