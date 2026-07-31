from tools.formatter_tool import FormatterTool





class CodeRepairTool:


    def __init__(
        self,
        llm
    ):

        self.llm = llm

        self.formatter = FormatterTool()






    def execute(
        self,
        plan
    ):


        code = plan


        if isinstance(code, dict):

            code = (
                code.get("code")
                or code.get("input")
                or code.get("context")
                or ""
            )



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