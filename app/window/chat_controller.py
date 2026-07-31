from PySide6.QtCore import QTimer

from app.worker import AIWorker
from app.chat_widget import MessageBubble




class ChatController:


    @staticmethod
    def connect(window):


        window.input.returnPressed.connect(
            window.send_message
        )


        window.button.clicked.connect(
            window.send_message
        )






    @staticmethod
    def add_message(
        window,
        text,
        user
    ):


        bubble = MessageBubble(
            text,
            user
        )


        window.chat_layout.addWidget(
            bubble
        )


        QTimer.singleShot(

            50,

            lambda:

            window.scroll.verticalScrollBar().setValue(

                window.scroll.verticalScrollBar().maximum()

            )

        )








    @staticmethod
    def send_message(window):


        if window.busy:

            return



        message = window.input.text().strip()



        if not message:

            return



        chat = window.chat_manager.get_chat(

            window.current_chat

        )



        if chat:


            if (

                chat.title == "New Chat"

                or

                chat.title.startswith("Chat")

            ):


                chat.rename(

                    message

                )


                window.chat_manager.save()



                from app.window.sidebar_controller import SidebarController


                SidebarController.refresh_chat_list(

                    window

                )






        window.last_user_message = message


        window.busy = True


        window.button.setEnabled(False)

        window.input.setEnabled(False)



        ChatController.add_message(

            window,

            message,

            True

        )


        window.input.clear()



        window.status.setText(

            "🤖 AI Thinking..."

        )




        window.worker = AIWorker(

            window.orchestrator,

            chat.conversation,

            message

        )




        window.worker.finished.connect(

            lambda response:

            ChatController.show_response(

                window,

                response

            )

        )


        window.worker.finished.connect(

            window.worker.deleteLater

        )


        window.worker.start()







    @staticmethod
    def show_response(

        window,

        response

    ):



        chat = window.chat_manager.get_chat(

            window.current_chat

        )


        if chat:


            chat.conversation.add(

                window.last_user_message,

                response

            )



        ChatController.add_message(

            window,

            response,

            False

        )



        window.status.setText(

            "🟢 Ready"

        )


        window.busy = False


        window.button.setEnabled(

            True

        )


        window.input.setEnabled(

            True

        )


        window.input.setFocus()