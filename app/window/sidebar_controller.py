from PySide6.QtWidgets import QListWidgetItem


class SidebarController:

    @staticmethod
    def connect(window):

        window.sidebar.chat_button.clicked.connect(
            lambda:
            SidebarController.show_chat_page(
                window
            )
        )

        window.sidebar.new_chat_button.clicked.connect(
            lambda:
            SidebarController.new_chat(
                window
            )
        )

        window.sidebar.chat_list.itemClicked.connect(
            lambda item:
            SidebarController.switch_chat(
                window,
                item
            )
        )

        window.sidebar.memory_button.clicked.connect(
            lambda:
            SidebarController.navigate(
                window,
                window.show_memory
            )
        )

        window.sidebar.history_button.clicked.connect(
            lambda:
            SidebarController.navigate(
                window,
                window.show_history
            )
        )

        window.sidebar.tools_button.clicked.connect(
            lambda:
            SidebarController.navigate(
                window,
                window.show_tools
            )
        )

        window.sidebar.formatter_button.clicked.connect(
            lambda:
            SidebarController.navigate(
                window,
                lambda:
                window.pages.setCurrentIndex(5)
            )
        )

        window.sidebar.settings_button.clicked.connect(
            lambda:
            SidebarController.navigate(
                window,
                lambda:
                window.pages.setCurrentIndex(4)
            )
        )

        SidebarController.refresh_chat_list(
            window
        )

    # =========================================================
    # NAVIGATION
    # =========================================================

    @staticmethod
    def hide_chat_section(window):

        window.sidebar.chat_list.hide()

        window.sidebar.new_chat_button.hide()

    @staticmethod
    def show_chat_page(window):

        window.sidebar.new_chat_button.show()

        window.sidebar.chat_list.show()

        window.pages.setCurrentIndex(0)

    @staticmethod
    def navigate(window, callback):

        SidebarController.hide_chat_section(
            window
        )

        callback()

    # =========================================================
    # CHAT LIST
    # =========================================================

    @staticmethod
    def refresh_chat_list(window):

        window.sidebar.chat_list.clear()

        for chat in window.chat_manager.list_chats():

            item = QListWidgetItem(
                f"💬 {chat.title}"
            )

            item.setData(
                256,
                chat.id
            )

            window.sidebar.chat_list.addItem(
                item
            )

    # =========================================================
    # CHAT
    # =========================================================

    @staticmethod
    def clear_chat(window):

        while window.chat_layout.count():

            item = (
                window.chat_layout.takeAt(0)
            )

            widget = item.widget()

            if widget:

                widget.deleteLater()

    @staticmethod
    def load_chat(window, chat):

        SidebarController.clear_chat(
            window
        )

        for message in chat.conversation.get():

            window.add_message(
                message.get(
                    "user",
                    ""
                ),
                True
            )

            window.add_message(
                message.get(
                    "assistant",
                    ""
                ),
                False
            )

    @staticmethod
    def new_chat(window):

        chat = (
            window.chat_manager.create_chat()
        )

        window.current_chat = chat.id

        window.conversation = (
            chat.conversation
        )

        SidebarController.clear_chat(
            window
        )

        window.add_message(
            """
🤖 AI-Studio-Agent

Merhaba! Size nasıl yardımcı olabilirim?

Sorularınızı sorabilir,
dosyalarınızı analiz ettirebilir
ve araçları kullanarak görev çalıştırabilirsiniz.
""",
            False
        )

        SidebarController.refresh_chat_list(
            window
        )

        SidebarController.show_chat_page(
            window
        )

    @staticmethod
    def switch_chat(window, item):

        chat_id = item.data(256)

        chat = window.chat_manager.get_chat(
            chat_id
        )

        if not chat:

            return

        window.current_chat = chat.id

        window.conversation = (
            chat.conversation
        )

        SidebarController.load_chat(
            window,
            chat
        )

        SidebarController.show_chat_page(
            window
        )