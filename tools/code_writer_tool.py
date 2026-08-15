from pathlib import Path

from app.core.logger import AppLogger



class CodeWriterTool:


    name = "code_writer"


    description = (
        "Applies CodeAgent implementation plans "
        "by generating and writing code changes."
    )

    purpose = (
        "Modify existing project source files."
    )

    safe = False

    modifies_files = True

    requires_confirmation = True

    version = "1.0"


    def __init__(
        self,
        llm,
        workspace=None
    ):

        self.llm = llm
        self.workspace = workspace
        self.logger = AppLogger()



    def execute(
        self,
        plan
    ):


        if not isinstance(plan, dict):

            return {
                "success": False,
                "message": "Invalid plan."
            }



        files = plan.get(
            "files",
            []
        )


        results = []



        for file in files:


            path = file.get(
                "path"
            )


            changes = file.get(
                "changes",
                []
            )


            if not path:
                continue



            result = self.modify_file(
                path,
                changes
            )


            results.append(
                result
            )



        return {
            "success": True,
            "results": results
        }





    def modify_file(
        self,
        filename,
        changes
    ):


        path = (
            Path(self.workspace)
            /
            filename
        )



        if not path.exists():

            return {
                "file": filename,
                "error": "File not found"
            }



        old_code = path.read_text(
            encoding="utf-8"
        )



        prompt = f"""

You are a senior Python developer.

Modify this existing file.

Current code:

{old_code}


Required changes:

{changes}


Rules:

- Preserve architecture.
- Return ONLY complete Python code.
- Do not explain.
- Do not remove existing features.

"""


        new_code = self.llm.generate(
            prompt
        )



        if new_code.startswith(
            "LLM_ERROR"
        ):

            return {
                "file": filename,
                "error": new_code
            }



        path.write_text(
            new_code,
            encoding="utf-8"
        )



        self.logger.info(
            f"Code updated: {path}"
        )


        return {
            "file": filename,
            "status": "updated"
        }