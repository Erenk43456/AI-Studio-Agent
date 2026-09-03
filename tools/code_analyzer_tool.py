import json
import re
from pathlib import Path

from app.core.logger import AppLogger


class CodeAnalyzerTool:

    name = "code_analyzer"

    description = (
        "Analyzes Python source code from files"
    )

    purpose = (
        "Analyze Python source code for syntax, logic, security, performance, and architecture issues."
    )

    safe = True

    modifies_files = False

    requires_confirmation = False

    version = "1.0" 



    """
    Static and AI based Python code analyzer.

    Responsibilities:
    - Read workspace files
    - Analyze Python code
    - Return structured JSON analysis
    """


    name = "code_analyzer"


    description = (
        "Analyzes Python code for syntax, logic, "
        "security and architecture issues."
    )



    def __init__(
        self,
        llm,
        workspace=None
    ):

        self.llm = llm
        self.workspace = workspace
        self.logger = AppLogger()

        # Token kontrolü için
        self.max_code_length = 12000



    def execute(
        self,
        plan
    ):


        try:


            if isinstance(plan, dict):


                filename = plan.get(
                    "filename",
                    ""
                )


                if filename and self.workspace:


                    workspace_path = Path(self.workspace).resolve()
                    file_path = (workspace_path / filename).resolve()

                    try:
                        file_path.relative_to(workspace_path)
                    except ValueError:
                        return {
                            "success": False,
                            "error": "File is outside workspace",
                            "file": filename,
                        }

                    if not file_path.exists():

                        return {

                            "success": False,

                            "error": "File not found",

                            "file": filename

                        }



                    code = file_path.read_text(

                        encoding="utf-8"

                    )


                    result = self.analyze_code(
                        code
                    )


                    result["file"] = filename


                    return result



                code = (

                    plan.get("code")
                    or
                    plan.get("context")
                    or
                    plan.get("content")
                    or ""

                )


            else:

                code = str(plan)



            return self.analyze_code(
                code
            )



        except Exception as error:


            self.logger.error(

                f"Analyzer execution error: {error}"

            )


            return {

                "success": False,

                "error": str(error)

            }





    def analyze_code(
        self,
        code
    ):


        if not code:


            return {

                "success": False,

                "error": "Code is empty."

            }



        #
        # Büyük dosya koruması
        #

        truncated = False
        original_code_length = len(code)

        if len(code) > self.max_code_length:

            code = code[:self.max_code_length]
            truncated = True

            self.logger.warning(
                "Code truncated because it was too large."
            )





        prompt = f"""

You are a senior Python software architect.

Analyze this Python code.

Return ONLY JSON.
No markdown.
No explanation outside JSON.

Required JSON format:

{{
    "summary": "",
    "syntax_errors": [],
    "logical_errors": [],
    "security_issues": [],
    "performance_issues": [],
    "architecture_issues": [],
    "improvements": [],
    "risk_level": "low"
}}


Python code:

----------------

{code}

----------------

"""



        try:


            response = self.llm.generate(
                prompt,
                max_tokens=2000,
                temperature=0.2,
                timeout=60
            )



            if not response:


                return {

                    "success": False,

                    "error": "Empty LLM response."

                }



            if isinstance(response, dict):
                if response.get("error"):
                    self.logger.error(
                        f"LLM response error: {response}"
                    )
                    
                    return {
                        "success": False,
                        "error": response.get("error")
                    }

                analysis = response

            else:
                if response.startswith("LLM_ERROR"):
                    return {
                        "success": False,
                        "error": response
                    }

                analysis = self.clean_json(response)


            self.logger.info(
                f"Code analyzer result: {analysis}"
            )


            result = {
                "success": True,
                "analysis": analysis,
            }

            if truncated:
                result.update({
                    "truncated": True,
                    "original_code_length": original_code_length,
                    "analyzed_code_length": len(code),
                })

            return result





        except Exception as error:


            self.logger.error(

                f"Code analysis error: {error}"

            )


            return {

                "success": False,

                "error": str(error)

            }


    @staticmethod
    def get_analysis_status(analysis):
        if not isinstance(analysis, dict):
            return "fail"

        if analysis.get("parse_error"):
            return "fail"

        blocking_fields = (
            "syntax_errors",
            "logical_errors",
            "security_issues",
            "architecture_issues",
        )

        for field in blocking_fields:
            if analysis.get(field):
                return "fail"

        if analysis.get("risk_level") in {
            "high",
            "critical",
        }:
            return "fail"

        return "pass"


    def clean_json(
        self,
        text
    ):


        if not text:

            return "{}"
        
        if isinstance(text, dict):
            return text


        text = str(text).strip()



        #
        # Markdown temizleme
        #

        text = text.replace(
            "```json",
            ""
        )


        text = text.replace(
            "```",
            ""
        )



        #
        # JSON bloğunu bul
        #

        match = re.search(

            r"\{.*\}",

            text,

            re.DOTALL

        )



        if match:

            text = match.group()



        try:


            return json.loads(
                text
            )



        except Exception:


            return {


                "raw_response": text,

                "parse_error": True

            }