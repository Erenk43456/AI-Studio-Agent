from pathlib import Path

from tools.formatter_tool import FormatterTool



class CodeRepairTool:


    def __init__(
        self,
        llm,
        workspace=None
    ):


        self.llm = llm

        self.workspace = workspace

        self.formatter = FormatterTool(

            workspace
            
        )



    def execute(
        self,
        plan
    ):


        if isinstance(plan, dict):


            filename = plan.get(
                "filename"
            )


            if filename and self.workspace:


                file_path = (

                    Path(self.workspace)
                    /
                    filename

                )


                if file_path.exists():


                    code = file_path.read_text(

                        encoding="utf-8"

                    )


                    result = self.repair_code(

                        code

                    )


                    if result.get("success"):


                        file_path.write_text(

                            result["code"],

                            encoding="utf-8"

                        )


                        result["file"] = str(

                            file_path

                        )


                    return result




            code = (

                plan.get("code")
                or plan.get("input")
                or plan.get("context")
                or ""

            )


        else:


            code = plan





        return self.repair_code(

            code

        )








    def repair_code(
        self,
        code
    ):


        if not code:


            return {

                "success": False,

                "message": "Code is empty."

            }






        prompt = f"""
You are a Python code repair assistant.

Fix all syntax and logical errors in this Python code.

Rules:
- Return ONLY corrected Python code.
- Do not add explanations.
- Keep the original purpose of the code.

Code:

{code}
"""



        response = self.llm.generate(

            prompt

        )





        if response.startswith(

            "LLM_ERROR"

        ):


            return {

                "success": False,

                "message": response

            }






        formatted = self.formatter.format_code(

            response

        )



        return {

            "success": True,

            "code": formatted

        }