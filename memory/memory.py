import json
from pathlib import Path
from datetime import datetime

from app.core.logger import AppLogger




class Memory:


    def __init__(self):


        self.logger = AppLogger()


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



                self.logger.info(

                    "Memory loaded successfully."

                )



            except json.JSONDecodeError as error:


                self.logger.error(

                    f"Memory JSON error: {error}"

                )


                self.data = {}



        else:


            self.data = {}


            self.logger.info(

                "New memory created."

            )









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



        self.logger.info(

            f"Memory saved: {key}"

        )









    def update(

        self,

        key,

        value

    ):



        if (

            key in self.data

            and isinstance(

                self.data[key],

                dict

            )

        ):



            self.data[key]["value"] = value


            self.data[key]["updated"] = self._timestamp()



            self.logger.info(

                f"Memory updated: {key}"

            )



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


            self.logger.warning(

                f"Memory not found: {key}"

            )


            return None





        if (

            isinstance(

                item,

                dict

            )

            and "value" in item

        ):


            return item["value"]





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



            self.logger.info(

                f"Memory deleted: {key}"

            )


            return True





        self.logger.warning(

            f"Delete failed, memory not found: {key}"

        )


        return False











    def clear(self):


        self.data = {}


        self._write()



        self.logger.info(

            "All memory cleared."

        )









    def recall(self):


        return self.data











    def _write(self):


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

                f"Memory write error: {error}"

            )