import json
from pathlib import Path
from datetime import datetime



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




    def _timestamp(self):

        return datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )





    def save(
        self,
        key,
        value,
        category="general"
    ):


        now = self._timestamp()



        self.data[key] = {

            "value": value,

            "category": category,

            "created": now,

            "updated": now

        }



        self._write()




    def update(
        self,
        key,
        value
    ):


        if key in self.data and isinstance(
            self.data[key],
            dict
        ):


            self.data[key]["value"] = value

            self.data[key]["updated"] = self._timestamp()



        else:

            self.save(
                key,
                value
            )



        self._write()




    def get(
        self,
        key
    ):


        item = self.data.get(
            key
        )


        if item is None:

            return None



        # Yeni format

        if isinstance(
            item,
            dict
        ) and "value" in item:

            return item["value"]



        # Eski format desteği

        return item




    def get_full(
        self,
        key
    ):

        return self.data.get(
            key
        )





    def delete(
        self,
        key
    ):


        if key in self.data:

            del self.data[key]

            self._write()

            return True



        return False





    def recall(self):

        return self.data




    def _write(self):


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