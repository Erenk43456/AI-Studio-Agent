import json
from pathlib import Path



class ConfigManager:


    def __init__(self):

        self.file = Path(
            "config/settings.json"
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






    def all(self):

        return self.data