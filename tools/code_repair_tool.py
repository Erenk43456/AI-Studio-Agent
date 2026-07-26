from models.llm_provider import LLMProvider
from config.config_manager import ConfigManager

from tools.formatter_tool import FormatterTool





class CodeRepairTool:


    def __init__(self):


        config = ConfigManager()


        self.llm = LLMProvider(
            config
        )


        self.formatter = FormatterTool()





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