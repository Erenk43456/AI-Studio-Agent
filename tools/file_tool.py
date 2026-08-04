from pathlib import Path
import shutil
import uuid
import os
import tempfile

from app.core.logger import AppLogger


class FileTool:

    name = "file"

    description = (
        "Secure workspace file operations."
    )


    def __init__(
        self,
        workspace=None
    ):

        self.logger = AppLogger()

        if workspace:

            self.base_path = Path(
                workspace
            ).resolve()

        else:

            self.base_path = Path.cwd().resolve()



        self.logger.info(
            f"FileTool workspace: {self.base_path}"
        )



    def execute(
        self,
        plan
    ):


        if not isinstance(plan, dict):

            return {

                "success": False,

                "error": "Invalid file request."

            }



        action = plan.get(
            "action",
            "read"
        )



        if action == "create":

            return self.create_file(
                plan.get("filename"),
                plan.get("content", "")
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



        return {

            "success": False,

            "error": f"Unknown action: {action}"

        }





    def get_path(
        self,
        filename
    ):


        if not filename:

            return None



        try:

            path = (
                self.base_path
                /
                Path(filename)
            ).resolve()



            path.relative_to(
                self.base_path
            )



            return path



        except ValueError:

            raise PermissionError(
                "Access outside workspace denied."
            )





    def create_file(
        self,
        filename,
        content=""
    ):


        try:

            path = self.get_path(
                filename
            )


            if path is None:

                return {

                    "success": False,

                    "error": "Filename missing."

                }



            path.parent.mkdir(
                parents=True,
                exist_ok=True
            )



            self.atomic_write(
                path,
                content or ""
            )



            self.logger.info(
                f"File created: {path}"
            )



            return {

                "success": True,

                "action": "create",

                "file": str(path),

                "message": "File created."

            }



        except Exception as error:


            self.logger.error(
                f"Create error: {error}"
            )


            return {

                "success": False,

                "error": str(error)

            }





    def create_backup(
        self,
        path
    ):


        if not path.exists():

            return None



        backup = Path(
            str(path)
            +
            f".backup_{uuid.uuid4().hex}"
        )



        shutil.copy2(
            path,
            backup
        )


        self.logger.info(
            f"Backup created: {backup}"
        )


        return backup





    def write_file(
        self,
        filename,
        content
    ):


        try:


            path = self.get_path(
                filename
            )



            if path is None:

                return {

                    "success": False,

                    "error": "Filename missing."

                }




            if content is None:

                return {

                    "success": False,

                    "error": "Empty content blocked."

                }



            if "<existing content>" in content:


                return {

                    "success": False,

                    "error":
                    "Incomplete generated content."

                }




            backup = self.create_backup(
                path
            )



            self.atomic_write(
                path,
                content
            )



            self.logger.info(
                f"File written: {path}"
            )



            return {

                "success": True,

                "action": "write",

                "file": str(path),

                "backup":
                    str(backup)
                    if backup
                    else None,

                "message":
                    "File updated."

            }



        except Exception as error:


            self.logger.error(
                f"Write error: {error}"
            )


            return {

                "success": False,

                "error": str(error)

            }





    def read_file(
        self,
        filename
    ):


        try:


            path = self.get_path(
                filename
            )



            if path is None:

                return {

                    "success": False,

                    "error": "Filename missing."

                }




            if not path.exists():

                return {

                    "success": False,

                    "error":
                    f"File not found: {filename}"

                }




            content = path.read_text(
                encoding="utf-8"
            )



            return {

                "success": True,

                "action": "read",

                "file": str(path),

                "content": content

            }



        except Exception as error:


            return {

                "success": False,

                "error": str(error)

            }





    def atomic_write(
        self,
        path,
        content
    ):


        path.parent.mkdir(
            parents=True,
            exist_ok=True
        )


        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            delete=False,
            dir=str(path.parent)
        ) as temp:


            temp.write(
                content
            )

            temp.flush()

            os.fsync(
                temp.fileno()
            )


            temp_path = Path(
                temp.name
            )



        os.replace(
            temp_path,
            path
        )