from PySide6.QtWidgets import QWidget


from app.window.backend import Backend
from app.window.ui_builder import UIBuilder
from app.window.chat_controller import ChatController


from app.window.sidebar_controller import SidebarController
from app.window.history_controller import HistoryController
from app.window.memory_controller import MemoryController





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



        SidebarController.connect(
            self
        )



        HistoryController.connect(
            self
        )



        MemoryController.connect(
            self
        )



        self.show_welcome_message()









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