from PySide6.QtWidgets import QMessageBox

from pathlib import Path
from datetime import datetime




class HistoryController:


    @staticmethod
    def connect(window):


        window.history_page.clear_button.clicked.connect(

            lambda:

            HistoryController.clear_history(window)

        )



        window.history_page.export_button.clicked.connect(

            lambda:

            HistoryController.export_history(window)

        )








    @staticmethod
    def clear_history(window):


        reply = QMessageBox.question(

            window,

            "Clear History",

            "Are you sure you want to delete all conversation history?",

            QMessageBox.Yes |

            QMessageBox.No

        )



        if reply != QMessageBox.Yes:

            return





        window.conversation.clear()



        window.history_page.update_history(

            window.conversation.get()

        )









    @staticmethod
    def export_history(window):


        conversations = window.conversation.get()



        if not conversations:


            QMessageBox.information(

                window,

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

            window,

            "Export Complete",

            f"History exported:\n{file_path}"

        )