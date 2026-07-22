from PySide6.QtWidgets import QMessageBox




class MemoryController:


    @staticmethod
    def connect(window):


        window.memory_page.refresh_button.clicked.connect(

            lambda:

            MemoryController.refresh_memory(window)

        )



        window.memory_page.clear_button.clicked.connect(

            lambda:

            MemoryController.clear_memory(window)

        )









    @staticmethod
    def refresh_memory(window):


        window.memory_page.update_memory(

            window.memory.data

        )









    @staticmethod
    def clear_memory(window):


        reply = QMessageBox.question(

            window,

            "Clear Memory",

            "Are you sure you want to delete all memory data?",

            QMessageBox.Yes |

            QMessageBox.No

        )



        if reply != QMessageBox.Yes:

            return







        window.memory.clear()







        window.memory_page.update_memory(

            window.memory.data

        )



        QMessageBox.information(

            window,

            "Memory Cleared",

            "All memory data has been deleted."

        )