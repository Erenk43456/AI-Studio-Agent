from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class ToolsPage(QWidget):

    def __init__(self):

        super().__init__()


        layout = QVBoxLayout()



        self.label = QLabel(
            "🛠 Araçlar"
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


        text = "🛠 Araçlar\n\n"


        for tool in tools:

            text += "✓ " + tool + "\n"



        self.label.setText(
            text
        )