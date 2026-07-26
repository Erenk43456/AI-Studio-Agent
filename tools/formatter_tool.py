import re
import subprocess
import sys
from pathlib import Path



class FormatterTool:


    def clean_code(
        self,
        code
    ):

        if not code:

            return ""



        code = code.strip()



        match = re.search(

            r"```(?:python)?\s*(.*?)```",

            code,

            re.DOTALL

        )


        if match:

            code = match.group(1).strip()



        return code






    def format_code(
        self,
        code
    ):


        code = self.clean_code(
            code
        )



        if not code:

            return {

                "success": False,

                "message": "Code is empty."

            }




        temp_file = Path(
            "temp_formatter.py"
        )



        try:


            temp_file.write_text(

                code,

                encoding="utf-8"

            )



            result = subprocess.run(

                [

                    sys.executable,

                    "-m",

                    "black",

                    str(temp_file)

                ],

                capture_output=True,

                text=True

            )




            if result.returncode != 0:


                return {

                    "success": False,

                    "message": result.stderr

                }




            formatted_code = temp_file.read_text(

                encoding="utf-8"

            )



            return {

                "success": True,

                "code": formatted_code

            }





        except Exception as error:


            return {

                "success": False,

                "message": str(error)

            }





        finally:


            if temp_file.exists():

                temp_file.unlink()







    def format_file(
        self,
        file_path
    ):



        path = Path(
            file_path
        )



        if not path.exists():

            return {

                "success": False,

                "message": "File not found."

            }




        if path.suffix != ".py":

            return {

                "success": False,

                "message": "Only Python files supported."

            }





        try:


            result = subprocess.run(

                [

                    sys.executable,

                    "-m",

                    "black",

                    str(path)

                ],

                capture_output=True,

                text=True

            )




            if result.returncode == 0:


                return {

                    "success": True,

                    "message": "File formatted."

                }



            return {

                "success": False,

                "message": result.stderr

            }





        except Exception as error:


            return {

                "success": False,

                "message": str(error)

            }