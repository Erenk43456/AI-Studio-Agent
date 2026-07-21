import json
from pathlib import Path


class Memory:

    def __init__(self):

        self.data_dir = Path("data")

        self.data_dir.mkdir(
            exist_ok=True
        )

        self.file = self.data_dir / "memory.json"


        if self.file.exists():

            try:

                with open(
                    self.file,
                    "r",
                    encoding="utf-8"
                ) as f:

                    self.data = json.load(f)

            except json.JSONDecodeError:

                self.data = {}

        else:

            self.data = {}



    def save(
        self,
        key,
        value
    ):

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



    def get(
        self,
        key
    ):

        return self.data.get(key)



    def recall(self):

        return self.data