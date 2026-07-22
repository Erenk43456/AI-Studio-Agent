class SidebarController:


    @staticmethod
    def connect(window):


        window.sidebar.chat_button.clicked.connect(

            lambda:

            window.pages.setCurrentIndex(0)

        )


        window.sidebar.memory_button.clicked.connect(

            window.show_memory

        )


        window.sidebar.history_button.clicked.connect(

            window.show_history

        )


        window.sidebar.tools_button.clicked.connect(

            window.show_tools

        )


        window.sidebar.settings_button.clicked.connect(

            lambda:

            window.pages.setCurrentIndex(4)

        )