import json
import os


class Memory:

    def __init__(self):

        os.makedirs(
            "data",
            exist_ok=True
        )

        self.file = "data/memory.json"


        if os.path.exists(self.file):

            with open(
                self.file,
                "r",
                encoding="utf-8"
            ) as f:

                self.data = json.load(f)

        else:

            self.data = {}



    def save(self, key, value):

        self.data[key] = value


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



    def get(self, key):

        return self.data.get(key)



    def recall(self):

        return self.data