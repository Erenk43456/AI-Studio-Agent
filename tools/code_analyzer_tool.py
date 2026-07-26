from models.llm import LLM
from app.core.logger import AppLogger


class CodeAnalyzerTool:

    def __init__(self):

        self.llm = LLM()

        self.logger = AppLogger()


    def analyze_code(self, code):

        if not code:

            return {
                "success": False,
                "message": "Code is empty."
            }


        prompt = f"""
You are a professional Python code analyzer.

Analyze the following Python code.

Check:

1. Syntax errors
2. Logical errors
3. Security issues
4. Performance problems
5. Code quality issues
6. Possible improvements

Explain each issue clearly.

Provide a structured analysis with sections.

Code:

{code}
"""


        try:

            result = self.llm.generate(
                prompt
            )


            return {

                "success": True,

                "analysis": result

            }


        except Exception as error:


            self.logger.error(

                f"Code analyzer error: {error}"

            )


            return {

                "success": False,

                "message": str(error)

            }