from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel
)


class ToolsPage(QWidget):

    def __init__(self):

        super().__init__()


        layout = QVBoxLayout()


        self.label = QLabel()


        self.label.setStyleSheet(
            """
            QLabel {

                font-size:16px;
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


        self.update_tools([])




    def update_tools(
        self,
        tools
    ):


        text = """
🛠 Available Tools


"""


        for tool in tools:


            if tool == "calculator":

                text += """
🧮 Calculator

Status:
🟢 Active

Operations:
+  -  *  /

"""


            elif tool == "file":

                text += """
📁 File Manager

Status:
🟢 Active

Capabilities:
Read / Write Files

"""


            elif tool == "memory":

                text += """
🧠 Memory System

Status:
🟢 Active

Storage:
Local JSON

"""


            else:

                text += f"""
🔧 {tool}

Status:
🟢 Active

"""



        self.label.setText(
            text
        )