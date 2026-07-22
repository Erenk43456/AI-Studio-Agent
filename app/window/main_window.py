from PySide6.QtWidgets import QWidget, QMessageBox

from pathlib import Path
from datetime import datetime


from app.window.backend import Backend
from app.window.ui_builder import UIBuilder
from app.window.chat_controller import ChatController





class AIWindow(QWidget):


    def __init__(self):

        super().__init__()



        self.worker = None

        self.busy = False




        UIBuilder.setup_window(
            self
        )



        Backend.setup(
            self
        )



        UIBuilder.build(
            self
        )



        ChatController.connect(
            self
        )



        self.connect_sidebar()


        self.connect_history()



        self.show_welcome_message()









    def connect_sidebar(self):


        self.sidebar.chat_button.clicked.connect(

            lambda:

            self.pages.setCurrentIndex(0)

        )



        self.sidebar.memory_button.clicked.connect(

            self.show_memory

        )



        self.sidebar.history_button.clicked.connect(

            self.show_history

        )



        self.sidebar.tools_button.clicked.connect(

            self.show_tools

        )



        self.sidebar.settings_button.clicked.connect(

            lambda:

            self.pages.setCurrentIndex(4)

        )









    def connect_history(self):


        self.history_page.clear_button.clicked.connect(

            self.clear_history

        )



        self.history_page.export_button.clicked.connect(

            self.export_history

        )











    def clear_history(self):


        reply = QMessageBox.question(

            self,

            "Clear History",

            "Are you sure you want to delete all conversation history?",

            QMessageBox.Yes |

            QMessageBox.No

        )



        if reply != QMessageBox.Yes:

            return



        self.conversation.clear()



        self.history_page.update_history(

            self.conversation.get()

        )









    def export_history(self):


        conversations = self.conversation.get()



        if not conversations:


            QMessageBox.information(

                self,

                "Export History",

                "No conversation history available."

            )


            return






        export_dir = Path(
            "exports"
        )


        export_dir.mkdir(
            exist_ok=True
        )





        filename = (

            "conversation_"

            +

            datetime.now().strftime(

                "%Y-%m-%d_%H-%M-%S"

            )

            +

            ".txt"

        )




        file_path = export_dir / filename





        with open(

            file_path,

            "w",

            encoding="utf-8"

        ) as file:



            for item in conversations:



                file.write(

                    f"Time: {item.get('time','')}\n\n"

                    f"User:\n"

                    f"{item.get('user','')}\n\n"

                    f"AI:\n"

                    f"{item.get('assistant','')}\n"

                    f"\n----------------------\n\n"

                )






        QMessageBox.information(

            self,

            "Export Complete",

            f"History exported:\n{file_path}"

        )











    def add_message(
        self,
        text,
        user
    ):


        ChatController.add_message(

            self,

            text,

            user

        )









    def send_message(self):


        ChatController.send_message(

            self

        )









    def show_response(
        self,
        response
    ):


        ChatController.show_response(

            self,

            response

        )









    def show_welcome_message(self):


        self.add_message(

            """
🤖 AI-Studio-Agent

Local AI Assistant Ready.

Runtime: Ollama

How can I help you?
""",

            False

        )









    def show_memory(self):


        self.memory_page.update_memory(

            self.memory.data

        )



        self.pages.setCurrentWidget(

            self.memory_page

        )









    def show_history(self):


        self.history_page.update_history(

            self.conversation.get()

        )



        self.pages.setCurrentWidget(

            self.history_page

        )









    def show_tools(self):


        self.tools_page.update_tools(

            self.registry.list_tools()

        )



        self.pages.setCurrentWidget(

            self.tools_page

        )









    def closeEvent(
        self,
        event
    ):


        if self.worker:


            try:


                if self.worker.isRunning():

                    self.worker.stop()



            except RuntimeError:

                pass




        event.accept()