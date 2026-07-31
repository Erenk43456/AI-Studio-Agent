class CodeAnalyzerTool:


    def __init__(
        self,
        llm
    ):

        self.llm = llm







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



        return self.analyze_code(

            code

        )








    def analyze_code(
        self,
        code
    ):


        if not code:


            return {

                "success": False,

                "message": "Code is empty."

            }







        prompt = f"""
You are a professional Python code analyzer.

Analyze this Python code.

Return a detailed report containing:

1. Syntax errors
2. Logical errors
3. Security problems
4. Performance issues
5. Code quality improvements

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






        return {

            "success": True,

            "analysis": response

        }