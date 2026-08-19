import ast
from pathlib import Path

from app.core.logger import AppLogger


class ValidationTool:

    name = "validation"

    description = (
        "Validates Python files for syntax errors "
        "without modifying them."
    )

    purpose = (
        "Verify that generated or modified Python files "
        "are syntactically valid before they are committed."
    )

    safe = True

    modifies_files = False

    requires_confirmation = False

    version = "1.0"

    def __init__(
        self,
        workspace
    ):

        self.workspace = Path(
            workspace
        ).resolve()

        self.logger = AppLogger()

    def execute(
        self,
        data
    ):

        # ---------------------------------------------------------
        # Input validation
        # ---------------------------------------------------------

        if not isinstance(
            data,
            dict
        ):

            return {
                "success": False,
                "message": (
                    "Invalid validation request."
                )
            }

        files = data.get(
            "files"
        )

        if files is None:

            return {
                "success": False,
                "message": (
                    "No files were provided."
                )
            }

        if not isinstance(
            files,
            list
        ):

            return {
                "success": False,
                "message": (
                    "Invalid files list."
                )
            }

        if not files:

            return {
                "success": False,
                "message": (
                    "No files were provided."
                )
            }

        # ---------------------------------------------------------
        # Validate files
        # ---------------------------------------------------------

        results = []

        overall_valid = True

        for file_path in files:

            result = self._validate_file(
                file_path
            )

            results.append(
                result
            )

            if not result.get(
                "valid",
                False
            ):

                overall_valid = False

        self.logger.info(
            "Validation completed: "
            f"{len(results)} file(s), "
            f"valid={overall_valid}"
        )

        return {
            "success": True,
            "valid": overall_valid,
            "results": results
        }

    def _validate_file(
        self,
        file_path
    ):

        # ---------------------------------------------------------
        # Validate path input
        # ---------------------------------------------------------

        if not isinstance(
            file_path,
            str
        ):

            return {
                "file": str(
                    file_path
                ),
                "valid": False,
                "error": (
                    "Invalid file path."
                )
            }

        if not file_path.strip():

            return {
                "file": file_path,
                "valid": False,
                "error": (
                    "Invalid file path."
                )
            }

        # ---------------------------------------------------------
        # Resolve target
        # ---------------------------------------------------------

        target = (
            self.workspace
            / file_path
        ).resolve()

        # ---------------------------------------------------------
        # Workspace isolation
        # ---------------------------------------------------------

        try:

            target.relative_to(
                self.workspace
            )

        except ValueError:

            self.logger.warning(
                "Validation target is outside "
                f"workspace: {file_path}"
            )

            return {
                "file": file_path,
                "valid": False,
                "error": (
                    "Path is outside the workspace."
                )
            }

        # ---------------------------------------------------------
        # File existence
        # ---------------------------------------------------------

        if not target.exists():

            return {
                "file": file_path,
                "valid": False,
                "error": (
                    "File not found."
                )
            }

        # ---------------------------------------------------------
        # Ensure target is a file
        # ---------------------------------------------------------

        if not target.is_file():

            return {
                "file": file_path,
                "valid": False,
                "error": (
                    "Target is not a file."
                )
            }

        # ---------------------------------------------------------
        # Python validation
        # ---------------------------------------------------------

        if target.suffix.lower() != ".py":

            return {
                "file": file_path,
                "valid": False,
                "error": (
                    "Unsupported file type."
                )
            }

        try:

            source = target.read_text(
                encoding="utf-8"
            )

        except Exception as error:

            self.logger.error(
                "Failed to read validation target "
                f"{target}: {error}"
            )

            return {
                "file": file_path,
                "valid": False,
                "error": str(
                    error
                )
            }

        # ---------------------------------------------------------
        # Python AST validation
        # ---------------------------------------------------------

        try:

            ast.parse(
                source,
                filename=str(
                    target
                )
            )

        except SyntaxError as error:

            message = self._format_syntax_error(
                error
            )

            self.logger.warning(
                f"Syntax validation failed: "
                f"{target}: {message}"
            )

            return {
                "file": file_path,
                "valid": False,
                "error": message
            }

        except Exception as error:

            self.logger.error(
                f"Validation failed: "
                f"{target}: {error}"
            )

            return {
                "file": file_path,
                "valid": False,
                "error": str(
                    error
                )
            }

        return {
            "file": file_path,
            "valid": True,
            "error": None
        }

    def _format_syntax_error(
        self,
        error
    ):

        message = str(
            error
        ).strip()

        if (
            getattr(
                error,
                "lineno",
                None
            ) is not None
        ):

            line = error.lineno

            if (
                getattr(
                    error,
                    "offset",
                    None
                ) is not None
            ):

                column = error.offset

                return (
                    f"Line {line}, "
                    f"column {column}: "
                    f"{message}"
                )

            return (
                f"Line {line}: "
                f"{message}"
            )

        return message