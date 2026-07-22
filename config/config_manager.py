import json
from pathlib import Path



class ConfigManager:


    def __init__(self):

        self.file = Path(
            "config/settings.json"
        )


        self.file.parent.mkdir(
            exist_ok=True
        )


        self.data = self.load()







    def load(self):


        if not self.file.exists():

            return {}



        try:


            with open(

                self.file,

                "r",

                encoding="utf-8"

            ) as f:


                return json.load(f)



        except json.JSONDecodeError:


            return {}









    def get(

        self,

        key,

        default=None

    ):


        return self.data.get(

            key,

            default

        )








    def set(

        self,

        key,

        value

    ):


        self.data[key] = value







    def update(

        self,

        values

    ):


        self.data.update(

            values

        )









    def save(self):


        with open(

            self.file,

            "w",

            encoding="utf-8"

        ) as f:


            json.dump(

                self.data,

                f,

                indent=4,

                ensure_ascii=False

            )









    def all(self):


        return self.data