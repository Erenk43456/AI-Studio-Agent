from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class ToolsPage(QWidget):

    def __init__(self):

        super().__init__()


        layout = QVBoxLayout()



        self.label = QLabel(
            "🛠 Tools"
        )


        self.label.setStyleSheet(
            """
            QLabel {
                font-size:18px;
                color:white;
            }
            """
        )


        layout.addWidget(
            self.label
        )


        self.setLayout(
            layout
        )



    def update_tools(
        self,
        tools
    ):


        text = "🛠 Tools\n\n"


        for tool in tools:

            text += "✓ " + tool + "\n"



        self.label.setText(
            text
        )