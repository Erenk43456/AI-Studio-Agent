import os
import shutil
from datetime import datetime

from app.core.logger import AppLogger



class FileTool:


    def __init__(
        self,
        workspace=None
    ):


        self.logger = AppLogger()


        if workspace:

            self.base_path = os.path.abspath(
                workspace
            )


        else:

            self.base_path = os.path.abspath(
                os.getcwd()
            )



        self.logger.info(

            f"FileTool workspace: {self.base_path}"

        )









    def execute(
        self,
        plan
    ):


        if not isinstance(plan, dict):

            return "Invalid file request."



        action = plan.get(

            "action",

            "read"

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


        if not filename:

            return None



        filename = filename.replace(

            "/",

            os.sep

        )



        path = os.path.abspath(

            os.path.join(

                self.base_path,

                filename

            )

        )



        workspace = os.path.abspath(

            self.base_path

        )



        if not path.startswith(

            workspace

        ):


            raise PermissionError(

                "Access outside workspace denied."

            )



        return path














    def create_file(
        self,
        filename,
        content=""
    ):


        try:


            path = self.get_path(

                filename

            )



            if not path:

                return "Filename missing."





            folder = os.path.dirname(

                path

            )



            os.makedirs(

                folder,

                exist_ok=True

            )





            with open(

                path,

                "w",

                encoding="utf-8"

            ) as file:


                file.write(

                    content or ""

                )





            self.logger.info(

                f"File created: {path}"

            )



            return f"File created: {path}"






        except Exception as error:


            return f"File error: {error}"














    def create_backup(
        self,
        path
    ):


        if not os.path.exists(path):

            return None



        backup_path = (

            path +

            ".backup_" +

            datetime.now().strftime(

                "%Y%m%d_%H%M%S"

            )

        )



        shutil.copy2(

            path,

            backup_path

        )



        self.logger.info(

            f"Backup created: {backup_path}"

        )



        return backup_path














    def write_file(
        self,
        filename,
        content
    ):


        try:


            path = self.get_path(

                filename

            )



            if not path:

                return "Filename missing."



            if content is None:

                return "Write blocked: empty content."



            if not content.strip():

                return "Write canceled: empty content."



            if "<existing content>" in content:

                return "Write blocked: incomplete generated content."



            backup = self.create_backup(

                path

            )



            with open(

                path,

                "w",

                encoding="utf-8"

            ) as file:


                file.write(

                    content

                )





            self.logger.info(

                f"File written: {path}"

            )



            return (

                f"File updated: {path}"

                +

                (

                    f" | Backup: {backup}"

                    if backup

                    else ""

                )

            )








        except Exception as error:


            return f"File error: {error}"














    def read_file(
        self,
        filename
    ):


        try:


            path = self.get_path(

                filename

            )



            if not path:

                return "Filename missing."





            with open(

                path,

                "r",

                encoding="utf-8"

            ) as file:


                return file.read()







        except FileNotFoundError:


            return f"File not found: {filename}"





        except Exception as error:


            return f"File error: {error}"