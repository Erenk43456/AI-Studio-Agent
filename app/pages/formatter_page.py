from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
    QApplication
)

from tools.formatter_tool import FormatterTool



class FormatterPage(QWidget):


    def __init__(self):

        super().__init__()


        self.formatter = FormatterTool()


        layout = QVBoxLayout()



        title = QLabel(
            "🧹 Python Formatter"
        )


        layout.addWidget(
            title
        )



        self.input_box = QTextEdit()

        self.input_box.setPlaceholderText(
            "Python kodunu buraya yapıştır..."
        )


        layout.addWidget(
            self.input_box
        )



        self.button = QPushButton(
            "Format Code"
        )


        self.button.clicked.connect(
            self.format_code
        )


        layout.addWidget(
            self.button
        )


        self.copy_button = QPushButton(
            "📋 Copy Code"
        )


        self.copy_button.clicked.connect(
            self.copy_code
        )


        layout.addWidget(
            self.copy_button
        )


        self.output_box = QTextEdit()

        self.output_box.setReadOnly(
            True
        )


        layout.addWidget(
            self.output_box
        )



        self.setLayout(
            layout
        )





    def format_code(self):


        code = self.input_box.toPlainText()


        result = self.formatter.format_code(
            code
        )


        if result["success"]:


            self.output_box.setPlainText(

                result["code"]

            )


        else:


            self.output_box.setPlainText(

                result["message"]

            )

    def copy_code(self):

        code = self.output_box.toPlainText()


        if code:

            QApplication.clipboard().setText(
                code
            )