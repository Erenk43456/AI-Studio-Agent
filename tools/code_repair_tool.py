from pathlib import Path

from tools.formatter_tool import FormatterTool
from tools.file_tool import FileTool


class CodeRepairTool:

    name = "code_repair"

    description = (
        "Repairs Python syntax and logical errors "
        "using an LLM and formats the resulting code."
    )

    purpose = (
        "Repair broken Python source code."
    )

    safe = False

    modifies_files = True

    requires_information = True

    version = "1.3"

    MAX_REPAIR_ATTEMPTS = 2

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

        self.file_tool = FileTool(
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

            # -----------------------------------------------------
            # IMPORTANT:
            # If CodeWriter supplied generated code, repair THAT
            # code instead of reading the old file from disk.
            # -----------------------------------------------------

            supplied_code = (
                plan.get("code")
                or plan.get("input")
            )

            context = (
                plan.get("context")
                or "Repair the broken Python code."
            )

            if supplied_code:

                result = self.repair_code(
                    supplied_code,
                    context
                )

                if result.get("success"):

                    result["file"] = filename

                return result

            # -----------------------------------------------------
            # Direct file repair mode
            # -----------------------------------------------------

            if filename and self.workspace:

                read_result = self.file_tool.read_file(
                    filename
                )

                if not read_result.get("success"):
                    return {
                        "success": False,
                        "message": read_result.get(
                            "error",
                            "Failed to read file."
                        ),
                        "file": filename
                    }

                code = read_result.get(
                    "content",
                    ""
                )

                result = self.repair_code(
                    code,
                    context
                )

                if not result.get("success"):
                    result["file"] = filename
                    return result

                write_result = self.file_tool.write_file(
                    filename,
                    result.get("code")
                )

                if not write_result.get("success"):
                    return {
                        "success": False,
                        "message": write_result.get(
                            "error",
                            "Failed to write repaired file."
                        ),
                        "file": filename
                    }

                result["file"] = write_result.get(
                    "file",
                    filename
                )

                result["backup"] = write_result.get(
                    "backup"
                )

                return result

            code = (
                plan.get("code")
                or plan.get("input")
                or plan.get("context")
                or ""
            )

            return self.repair_code(
                code,
                context
            )

        return self.repair_code(
            plan,
            "Repair the broken Python code."
        )

    def repair_code(
        self,
        code,
        context=None
    ):

        if not isinstance(
            code,
            str
        ):

            return {
                "success": False,
                "message": "Invalid code input."
            }

        code = code.strip()

        if not code:

            return {
                "success": False,
                "message": "Code is empty."
            }

        context = (
            context
            or
            "Repair the broken Python code."
        )

        current_code = code
        last_error = None

        # =========================================================
        # REPAIR ATTEMPTS
        # =========================================================

        for attempt in range(
            1,
            self.MAX_REPAIR_ATTEMPTS + 1
        ):

            if attempt == 1:

                prompt = self.build_repair_prompt(
                    current_code,
                    context
                )

            else:

                prompt = self.build_retry_prompt(
                    current_code,
                    context,
                    last_error
                )

            try:

                response = self.llm.generate(
                    prompt
                )

            except Exception as error:

                return {
                    "success": False,
                    "message": (
                        f"LLM repair failed: {error}"
                    )
                }

            if isinstance(
                response,
                dict
            ):

                return {
                    "success": False,
                    "message": (
                        f"LLM returned an error: {response}"
                    )
                }

            if not isinstance(
                response,
                str
            ):

                return {
                    "success": False,
                    "message": (
                        "LLM returned an invalid response type."
                    )
                }

            repaired_code = self.clean_code(
                response
            )

            if not repaired_code.strip():

                return {
                    "success": False,
                    "message": (
                        "LLM returned empty repaired code."
                    )
                }

            # -----------------------------------------------------
            # Validate generated code BEFORE formatting
            # -----------------------------------------------------

            syntax_error = self.validate_python(
                repaired_code
            )

            if syntax_error is not None:

                last_error = syntax_error
                current_code = repaired_code

                # If there is another attempt available,
                # retry with the syntax error included.
                if attempt < self.MAX_REPAIR_ATTEMPTS:
                    continue

                return {
                    "success": False,
                    "message": (
                        "Code repair returned invalid code."
                    ),
                    "details": syntax_error
                }

            # -----------------------------------------------------
            # Format only AFTER syntax is valid
            # -----------------------------------------------------

            formatted = self.formatter.format_code(
                repaired_code
            )

            if not formatted.get(
                "success",
                False
            ):

                last_error = formatted.get(
                    "message",
                    "Formatting failed."
                )

                current_code = repaired_code

                if attempt < self.MAX_REPAIR_ATTEMPTS:
                    continue

                return {
                    "success": False,
                    "message": (
                        "Repaired code could not be formatted."
                    ),
                    "details": last_error
                }

            repaired_code = formatted.get(
                "code",
                ""
            )

            if not isinstance(
                repaired_code,
                str
            ):

                last_error = (
                    "Formatter returned invalid code."
                )

                current_code = ""

                if attempt < self.MAX_REPAIR_ATTEMPTS:
                    continue

                return {
                    "success": False,
                    "message": (
                        "Formatter returned invalid code."
                    )
                }

            repaired_code = (
                repaired_code.strip()
                +
                "\n"
            )

            # -----------------------------------------------------
            # Validate AGAIN after formatting
            # -----------------------------------------------------

            syntax_error = self.validate_python(
                repaired_code
            )

            if syntax_error is not None:

                last_error = syntax_error
                current_code = repaired_code

                if attempt < self.MAX_REPAIR_ATTEMPTS:
                    continue

                return {
                    "success": False,
                    "message": (
                        "Formatted repaired code is invalid."
                    ),
                    "details": syntax_error
                }

            # -----------------------------------------------------
            # SUCCESS
            # -----------------------------------------------------

            return {
                "success": True,
                "code": repaired_code
            }

        # Should never be reached.
        return {
            "success": False,
            "message": (
                "Code repair failed after "
                f"{self.MAX_REPAIR_ATTEMPTS} attempts."
            ),
            "details": last_error
        }

    @staticmethod
    def build_repair_prompt(
        code,
        context
    ):

        return f"""
You are an expert Python code repair agent.

You are repairing Python source code generated by another
code-generation agent.

The generated code may contain:

- syntax errors
- missing brackets
- missing parentheses
- unterminated strings
- broken indentation
- malformed blocks
- incomplete try/except/finally blocks
- invalid imports
- accidentally deleted code
- incomplete functions or classes

Your primary goal is to produce COMPLETE, VALID Python code.

Repair the supplied code while preserving its original
architecture and intended functionality.

IMPORTANT RULES:

- Return ONLY complete Python source code.
- Do NOT return Markdown.
- Do NOT use code fences.
- Do NOT explain the changes.
- Do NOT return partial code.
- Do NOT remove existing classes or methods merely to make
  the code syntactically valid.
- Do NOT replace the entire architecture.
- Preserve existing imports when possible.
- Preserve existing classes.
- Preserve existing methods.
- Preserve constructor signatures unless the error itself
  requires a correction.
- Make the smallest reasonable repair.
- The result MUST be valid Python.
- The result MUST be complete.
- The result MUST be parseable by ast.parse().
- The result MUST be compilable by compile().
- Do not leave TODO placeholders instead of implementation.

Additional repair context:

{context}

==================================================
BROKEN PYTHON SOURCE
==================================================

{code}

==================================================
END SOURCE
==================================================

Return ONLY the repaired Python source code.
"""

    @staticmethod
    def build_retry_prompt(
        code,
        context,
        error
    ):

        return f"""
You are an expert Python code repair agent.

Your previous repair attempt produced INVALID Python code.

You MUST fix the syntax error and return a COMPLETE,
VALID Python source file.

IMPORTANT:

- Return ONLY Python source code.
- Do NOT return Markdown.
- Do NOT use code fences.
- Do NOT explain anything.
- Do NOT return partial code.
- Do NOT remove existing classes.
- Do NOT remove existing methods.
- Preserve existing imports.
- Preserve existing architecture.
- Preserve existing functionality.
- Make the smallest possible repair.
- The final result MUST compile successfully.
- The final result MUST be valid Python.
- Do not leave TODO placeholders.
- Do not simply repeat the previous invalid output.

Original repair context:

{context}

==================================================
SYNTAX ERROR FROM PREVIOUS ATTEMPT
==================================================

{error}

==================================================
PREVIOUS REPAIR OUTPUT
==================================================

{code}

==================================================
END PREVIOUS OUTPUT
==================================================

Return ONLY the corrected Python source code.
"""

    @staticmethod
    def validate_python(
        code
    ):

        try:

            compile(
                code,
                "<code_repair>",
                "exec"
            )

            return None

        except SyntaxError as error:

            return (
                f"{error.msg} "
                f"(line {error.lineno}, "
                f"column {error.offset})"
            )

        except Exception as error:

            return str(error)

    @staticmethod
    def clean_code(
        code
    ):

        if not isinstance(
            code,
            str
        ):

            return ""

        code = code.strip()

        if not code:

            return ""

        # ---------------------------------------------------------
        # Remove Markdown code fences if the LLM ignored the
        # output instructions.
        # ---------------------------------------------------------

        if code.startswith(
            "```"
        ):

            lines = code.splitlines()

            if lines:

                first_line = lines[0].strip()

                if first_line.startswith(
                    "```"
                ):

                    lines = lines[1:]

            if (
                lines
                and
                lines[-1].strip() == "```"
            ):

                lines = lines[:-1]

            code = "\n".join(
                lines
            )

        return code.strip() + "\n"