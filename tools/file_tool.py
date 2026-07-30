import os

from app.core.logger import AppLogger



class FileTool:


    def __init__(self):


        self.base_path = "data/files"

        self.logger = AppLogger()


        os.makedirs(

            self.base_path,

            exist_ok=True

        )








    def execute(
        self,
        plan
    ):


        action = plan.get(

            "action",

            "create"

        )




        if action == "create":


            return self.create_file(

                plan.get("filename"),

                plan.get("content")

            )





        if action == "write":


            return self.write_file(

                plan.get("filename"),

                plan.get("content")

            )





        if action == "read":


            return self.read_file(

                plan.get("filename")

            )





        return "Invalid file action."









    def get_path(
        self,
        filename
    ):


        return os.path.join(

            self.base_path,

            filename

        )









    def create_file(
        self,
        filename,
        content=""
    ):


        if not filename:


            return "Filename missing."




        path = self.get_path(

            filename

        )



        try:


            with open(

                path,

                "w",

                encoding="utf-8"

            ) as file:


                file.write(

                    content or ""

                )




            self.logger.info(

                f"File created: {filename}"

            )



            return f"File created: {filename}"






        except Exception as error:


            return f"File error: {error}"









    def write_file(
        self,
        filename,
        content
    ):


        if not filename:


            return "Filename missing."




        path = self.get_path(

            filename

        )




        try:


            with open(

                path,

                "w",

                encoding="utf-8"

            ) as file:


                file.write(

                    content or ""

                )




            self.logger.info(

                f"File written: {filename}"

            )



            return f"File updated: {filename}"






        except Exception as error:


            return f"File error: {error}"









    def read_file(
        self,
        filename
    ):


        if not filename:


            return "Filename missing."




        path = self.get_path(

            filename

        )



        try:


            with open(

                path,

                "r",

                encoding="utf-8"

            ) as file:


                return file.read()






        except FileNotFoundError:


            return "File not found."






        except Exception as error:


            return f"File error: {error}"