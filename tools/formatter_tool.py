"""Safe, dependency-free Python formatting helpers."""

from __future__ import annotations

import ast
from collections.abc import Mapping
from pathlib import Path
from typing import Any



class FormatterTool:
    """Format Python source supplied directly or inside a planner step."""



    def __init__(
        self,
        workspace=None
    ):

        self.workspace = workspace






    @staticmethod
    def _extract_code(
        value: str | Mapping[str, Any]
    ) -> str:


        if isinstance(value, str):

            return value


        if isinstance(value, Mapping):

            return str(

                value.get("code")
                or value.get("input")
                or value.get("context")
                or ""

            )


        return ""







    def execute(
        self,
        plan: str | Mapping[str, Any]
    ):



        if isinstance(plan, Mapping):


            filename = plan.get(
                "filename"
            )


            if filename and self.workspace:

                try:

                    workspace = Path(
                        self.workspace
                    ).resolve()

                    path = (
                        workspace /
                        Path(filename)
                    ).resolve()

                    path.relative_to(
                        workspace
                    )

                except ValueError:

                    return str({
                        "success": False,
                        "message": (
                            "Access outside workspace denied."
                        )
                    })

                except Exception as error:

                    return str({
                        "success": False,
                        "message": (
                            f"Invalid file path: {error}"
                        )
                    })

                result = self.format_file(
                    path,
                    write=True
                )

                return str(
                    result
                )



        result = self.format_code(

            plan

        )


        return str(

            result.get("code")
            if result["success"]
            else result["message"]

        )








    def format_code(
        self,
        value: str | Mapping[str, Any]
    ) -> dict[str, str | bool]:


        code = self._extract_code(

            value

        ).strip()



        if not code:

            return {

                "success": False,

                "message": "Code is empty."

            }



        try:


            return {

                "success": True,

                "code": ast.unparse(

                    ast.parse(code)

                )

            }



        except SyntaxError as error:


            return {

                "success": False,

                "message": f"Syntax error: {error}"

            }



        except Exception as error:


            return {

                "success": False,

                "message": f"Formatting error: {error}"

            }









    def format_file(
        self,
        file_path: str | Path,
        *,
        write: bool = False
    ) -> dict[str, str | bool]:


        path = Path(

            file_path

        )



        if not path.is_file():


            return {

                "success": False,

                "message": "File not found."

            }




        if path.suffix.lower() != ".py":


            return {

                "success": False,

                "message": "Only Python files are supported."

            }




        result = self.format_code(

            path.read_text(

                encoding="utf-8"

            )

        )



        if result["success"] and write:
            if self.workspace is not None:
                try:
                    workspace = Path(self.workspace).resolve()
                    path.resolve().relative_to(workspace)
                except ValueError:
                    return {
                        "success": False,
                        "message": "Access outside workspace denied."
                    }
                except Exception as error:
                    return {
                        "success": False,
                        "message": f"Invalid file path: {error}"
                    }

            path.write_text(
                f"{result['code']}\n",
                encoding="utf-8"
            )



        return result