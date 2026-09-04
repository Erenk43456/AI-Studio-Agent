import json
from pathlib import Path
from datetime import datetime

from app.core.logger import AppLogger



class ConversationMemory:


    def __init__(self, file_path=None):


        self.logger = AppLogger()


        if file_path:

            self.file = Path(file_path)

            self.file.parent.mkdir(
                exist_ok=True
            )


        else:

            self.data_dir = Path("data")

            self.data_dir.mkdir(
                exist_ok=True
            )

            self.file = (
                self.data_dir /
                "conversation.json"
            )



        if self.file.exists():

            try:

                with open(
                    self.file,
                    "r",
                    encoding="utf-8"
                ) as f:

                    data = json.load(f)

                self.data = data if isinstance(data, list) else []


                self.logger.info(
                    "Conversation history loaded."
                )


            except json.JSONDecodeError as error:

                self.logger.error(
                    f"Conversation JSON error: {error}"
                )

                self.data = []


        else:

            self.data = []

            self.logger.info(
                "New conversation history created."
            )




    def add(
        self,
        user,
        assistant
    ):


        self.data.append(

            {
                "user": user,
                "assistant": assistant,
                "time": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            }

        )


        self.data = self.data[-20:]


        self.save()


        self.logger.info(
            "Conversation added."
        )




    def save(self):

        try:

            with open(
                self.file,
                "w",
                encoding="utf-8"
            ) as f:


                json.dump(
                    self.data,
                    f,
                    ensure_ascii=False,
                    indent=4
                )


        except Exception as error:

            self.logger.error(
                f"Conversation save error: {error}"
            )

            raise




    def get(self):

        return self.data


    def get_last(
        self,
        count=5
    ):

        return self.data[-count:]




    def clear(self):

        self.data = []

        self.save()


        self.logger.info(
            "Conversation history cleared."
        )
