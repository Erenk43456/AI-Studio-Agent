from PySide6.QtWidgets import QStackedWidget


from app.pages.memory_page import MemoryPage
from app.pages.history_page import HistoryPage
from app.pages.tools_page import ToolsPage
from app.pages.settings_page import SettingsPage





class PageManager:



    @staticmethod
    def create(window):


        window.pages = QStackedWidget()



        window.chat_index = 0



        window.memory_page = MemoryPage()

        window.history_page = HistoryPage()

        window.tools_page = ToolsPage()

        window.settings_page = SettingsPage()





        window.pages.addWidget(
            window.scroll
        )


        window.pages.addWidget(
            window.memory_page
        )


        window.pages.addWidget(
            window.history_page
        )


        window.pages.addWidget(
            window.tools_page
        )


        window.pages.addWidget(
            window.settings_page
        )



        return window.pages