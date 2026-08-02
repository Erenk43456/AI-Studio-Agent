from pathlib import Path



class CodeAnalyzerTool:


    def __init__(
        self,
        llm,
        workspace=None
    ):


        self.llm = llm

        self.workspace = workspace







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


                    result = self.analyze_code(

                        code

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