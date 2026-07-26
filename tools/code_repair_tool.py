from models.llm import LLM
from tools.formatter_tool import FormatterTool



class CodeRepairTool:


    def __init__(self):

        self.llm = LLM()

        self.formatter = FormatterTool()





    def repair_code(
        self,
        code
    ):


        prompt = f"""
You are a Python code repair assistant.

Fix the errors in this code.

Return ONLY the corrected Python code.

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



        return formatted