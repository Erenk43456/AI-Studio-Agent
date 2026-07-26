import os
import subprocess
import sys



class FileTool:


    def create_file(
        self,
        filename,
        content
    ):


        if not filename:

            return "Filename not provided."



        try:


            with open(
                filename,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(
                    content or ""
                )



            format_result = self.format_file(
                filename
            )



            if format_result:

                return format_result



            return f"{filename} created successfully."



        except OSError as error:


            return f"File creation error: {error}"






    def write_file(
        self,
        filename,
        content
    ):


        if not filename:

            return "Filename not provided."



        try:


            with open(
                filename,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(
                    content
                )



            format_result = self.format_file(
                filename
            )



            if format_result:

                return format_result



            return f"{filename} updated successfully."



        except OSError as error:


            return f"File writing error: {error}"







    def read_file(
        self,
        filename
    ):


        if not filename:

            return "Filename not provided."



        if not os.path.exists(filename):

            return "File not found."



        try:


            with open(
                filename,
                "r",
                encoding="utf-8"
            ) as file:

                return file.read()



        except OSError as error:


            return f"File reading error: {error}"








    def format_file(
        self,
        filename
    ):


        if not filename.endswith(".py"):

            return None



        try:


            result = subprocess.run(

                [
                    sys.executable,
                    "-m",
                    "black",
                    filename
                ],

                capture_output=True,

                text=True

            )



            if result.returncode != 0:


                return (
                    f"Formatting failed:\n"
                    f"{result.stderr}"
                )



            return None



        except Exception as error:


            return (
                f"Formatter error: {error}"
            )