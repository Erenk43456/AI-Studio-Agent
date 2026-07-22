import json
from pathlib import Path
from datetime import datetime



class ConversationMemory:


    def __init__(self):

        self.data_dir = Path("data")


        self.data_dir.mkdir(
            exist_ok=True
        )


        self.file = self.data_dir / "conversation.json"



        if self.file.exists():

            try:

                with open(
                    self.file,
                    "r",
                    encoding="utf-8"
                ) as f:

                    self.data = json.load(f)


            except json.JSONDecodeError:

                self.data = []


        else:

            self.data = []





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



        # Son 20 konuşmayı tut

        self.data = self.data[-20:]



        self.save()






    def save(self):


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






    def get(self):

        return self.data





    def clear(self):


        self.data = []


        self.save()