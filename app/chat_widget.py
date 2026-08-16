from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout
)

from PySide6.QtCore import Qt


class MessageBubble(QWidget):

    def __init__(
        self,
        text,
        is_user=False
    ):

        super().__init__()

        layout = QHBoxLayout()

        layout.setContentsMargins(
            12,
            8,
            12,
            8
        )

        layout.setSpacing(
            0
        )

        self.label = QLabel(
            text
        )

        self.label.setWordWrap(
            True
        )

        self.label.setTextInteractionFlags(
            Qt.TextSelectableByMouse
        )

        self.label.setMaximumWidth(
            680
        )

        if is_user:

            self.label.setStyleSheet(
                """
                QLabel {
                    background-color: #3b82f6;
                    color: white;
                    padding: 11px 15px;
                    border-radius: 12px;
                    font-size: 13px;
                }
                """
            )

            layout.addStretch()

            layout.addWidget(
                self.label
            )

        else:

            self.label.setStyleSheet(
                """
                QLabel {
                    background-color: #1b1e22;
                    color: #e7e9ec;
                    padding: 11px 15px;
                    border: 1px solid #292d32;
                    border-radius: 12px;
                    font-size: 13px;
                }
                """
            )

            layout.addWidget(
                self.label
            )

            layout.addStretch()

        self.setLayout(
            layout
        )


class AIThinkingBubble(QWidget):

    STAGES = [
        "Preparing",
        "Thinking",
        "Generating",
        "Complete"
    ]

    def __init__(self):

        super().__init__()

        self.current_stage = 0

        self.setObjectName(
            "aiThinkingBubble"
        )

        main_layout = QVBoxLayout()

        main_layout.setContentsMargins(
            12,
            5,
            12,
            5
        )

        main_layout.setSpacing(
            4
        )

        self.status_label = QLabel(
            "● Preparing"
        )

        self.status_label.setStyleSheet(
            """
            QLabel {
                color: #8f969f;
                font-size: 11px;
                padding: 2px 0;
            }
            """
        )

        main_layout.addWidget(
            self.status_label
        )

        stages_layout = QHBoxLayout()

        stages_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        stages_layout.setSpacing(
            6
        )

        self.stage_labels = []

        for index, stage in enumerate(
            self.STAGES
        ):

            label = QLabel(
                f"○ {stage}"
            )

            label.setAlignment(
                Qt.AlignCenter
            )

            label.setStyleSheet(
                """
                QLabel {
                    color: #555c64;
                    background-color: transparent;
                    border: none;
                    font-size: 10px;
                    padding: 3px 5px;
                }
                """
            )

            stages_layout.addWidget(
                label
            )

            self.stage_labels.append(
                label
            )

        main_layout.addLayout(
            stages_layout
        )

        self.setLayout(
            main_layout
        )

        self.update_stage(
            0
        )

    # =========================================================
    # STAGE
    # =========================================================

    def update_stage(
        self,
        stage_index
    ):

        if stage_index < 0:

            stage_index = 0

        if stage_index >= len(
            self.STAGES
        ):

            stage_index = (
                len(self.STAGES) - 1
            )

        self.current_stage = stage_index

        for index, label in enumerate(
            self.stage_labels
        ):

            if index < stage_index:

                label.setText(
                    f"✓ {self.STAGES[index]}"
                )

                label.setStyleSheet(
                    """
                    QLabel {
                        color: #6fbd7b;
                        background-color: transparent;
                        border: none;
                        font-size: 10px;
                        padding: 3px 5px;
                    }
                    """
                )

            elif index == stage_index:

                label.setText(
                    f"● {self.STAGES[index]}"
                )

                label.setStyleSheet(
                    """
                    QLabel {
                        color: #5b9cff;
                        background-color: #192333;
                        border: 1px solid #29466f;
                        border-radius: 6px;
                        font-size: 10px;
                        padding: 3px 7px;
                    }
                    """
                )

            else:

                label.setText(
                    f"○ {self.STAGES[index]}"
                )

                label.setStyleSheet(
                    """
                    QLabel {
                        color: #555c64;
                        background-color: transparent;
                        border: none;
                        font-size: 10px;
                        padding: 3px 5px;
                    }
                    """
                )

        self.status_label.setText(
            f"●  {self.STAGES[stage_index]}"
        )