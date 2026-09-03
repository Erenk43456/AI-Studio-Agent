from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class ToolsPage(QWidget):

    def __init__(self):
        super().__init__()

        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout()
        root.setContentsMargins(18, 14, 18, 14)
        root.setSpacing(10)

        self.title = QLabel("Tools")
        self.title.setStyleSheet(
            """
            QLabel {
                font-size: 22px;
                font-weight: 600;
                color: #e7e9ec;
            }
            """
        )

        self.subtitle = QLabel("No tools available")
        self.subtitle.setStyleSheet(
            """
            QLabel {
                font-size: 13px;
                color: #7f8791;
            }
            """
        )

        root.addWidget(self.title)
        root.addWidget(self.subtitle)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.container = QWidget()

        self.grid = QGridLayout()
        self.grid.setContentsMargins(0, 8, 0, 8)
        self.grid.setHorizontalSpacing(10)
        self.grid.setVerticalSpacing(10)

        self.container.setLayout(self.grid)
        self.scroll.setWidget(self.container)

        root.addWidget(self.scroll)

        self.setLayout(root)

    def update_tools(self, tools):
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        if not tools:
            self.subtitle.setText("No tools available")
            return

        self.subtitle.setText(
            f"{len(tools)} tool{'s' if len(tools) != 1 else ''} available"
        )

        for index, tool in enumerate(tools):
            row = index // 2
            column = index % 2

            self.grid.addWidget(
                self._create_tool_card(tool),
                row,
                column,
            )

        self.grid.setColumnStretch(0, 1)
        self.grid.setColumnStretch(1, 1)

    def _create_tool_card(self, tool):
        card = QFrame()
        card.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed,
        )

        card.setStyleSheet(
            """
            QFrame {
                background: #191c20;
                border: 1px solid #30353b;
                border-radius: 10px;
            }

            QLabel {
                background: transparent;
                border: none;
            }
            """
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(7)

        name = tool.get("name", "Unknown")
        description = tool.get(
            "description",
            "No description provided.",
        )
        purpose = tool.get(
            "purpose",
            "",
        )

        name_label = QLabel(name)
        name_label.setStyleSheet(
            """
            QLabel {
                font-size: 15px;
                font-weight: 600;
                color: #e7e9ec;
            }
            """
        )

        description_label = QLabel(description)
        description_label.setWordWrap(True)
        description_label.setStyleSheet(
            """
            QLabel {
                font-size: 13px;
                color: #b8bec7;
            }
            """
        )

        layout.addWidget(name_label)
        layout.addWidget(description_label)

        if purpose:
            purpose_label = QLabel(purpose)
            purpose_label.setWordWrap(True)
            purpose_label.setStyleSheet(
                """
                QLabel {
                    font-size: 12px;
                    color: #7f8791;
                }
                """
            )

            layout.addWidget(purpose_label)

        status_layout = QGridLayout()
        status_layout.setHorizontalSpacing(8)
        status_layout.setVerticalSpacing(5)

        safe = tool.get("safe", True)
        modifies_files = tool.get(
            "modifies_files",
            False,
        )
        requires_confirmation = tool.get(
            "requires_confirmation",
            False,
        )

        status_layout.addWidget(
            self._status_label(
                "● Active",
                True,
            ),
            0,
            0,
        )

        status_layout.addWidget(
            self._status_label(
                "Safe" if safe else "Restricted",
                safe,
            ),
            0,
            1,
        )

        status_layout.addWidget(
            self._status_label(
                "Modifies files"
                if modifies_files
                else "Read-only",
                not modifies_files,
            ),
            1,
            0,
        )

        status_layout.addWidget(
            self._status_label(
                "Confirmation required"
                if requires_confirmation
                else "No confirmation",
                not requires_confirmation,
            ),
            1,
            1,
        )

        layout.addLayout(status_layout)

        card.setLayout(layout)

        return card

    def _status_label(self, text, positive):
        label = QLabel(text)

        label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 11px;
                color: {"#9ad6a5" if positive else "#e5a6a6"};
            }}
            """
        )

        return label