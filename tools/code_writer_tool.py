import ast
from pathlib import Path

from app.core.logger import AppLogger

from tools.atomic_writer import AtomicWriter


class CodeWriterTool:

    name = "code_writer"

    description = (
        "Applies CodeAgent implementation plans "
        "by generating and writing code changes safely."
    )

    purpose = (
        "Modify existing project source files while "
        "preserving architecture and public APIs."
    )

    safe = False

    modifies_files = True

    requires_confirmation = True

    version = "1.3"

    def __init__(
        self,
        llm,
        workspace=None,
        registry=None
    ):

        self.llm = llm
        self.workspace = workspace
        self.registry = registry
        self.logger = AppLogger()
        self.atomic_writer = (
            AtomicWriter(self.workspace)
            if self.workspace
            else None
        )
        self.current_development_context = {}

    def execute(
        self,
        plan
    ):

        if not isinstance(plan, dict):

            return {
                "success": False,
                "message": "Invalid plan."
            }

        self.current_development_context = plan.get(
            "development_context",
            {}
        )

        files = plan.get(
            "files",
            []
        )

        if not isinstance(files, list):

            return {
                "success": False,
                "message": "Invalid files list."
            }

        results = []
        snapshots = {}

        if not self.workspace:
        
            return {
                "success": False,
                "message": "Workspace is not configured.",
                "results": []
            }

        for file in files:

            if not isinstance(file, dict):
                continue

            path = file.get(
                "path"
            )

            changes = file.get(
                "changes",
                []
            )

            if not path:
                continue

            if not isinstance(
                changes,
                list
            ):
                continue
            
            if not changes:

                continue

            workspace_path = Path(
                self.workspace
            ).resolve()

            path_obj = (
                workspace_path
                / path
            ).resolve()

            try:
                path_obj.relative_to(
                    workspace_path
                )
            except ValueError:
                result = {
                    "file": path,
                    "error": "Path is outside the workspace."
                }
            else:
                try:
                    snapshots[str(path_obj)] = (
                        path_obj.read_bytes()
                        if path_obj.exists()
                        else None
                    )
                except Exception as error:
                    result = {
                        "file": path,
                        "error": (
                            f"Failed to snapshot file before write: {error}"
                        )
                    }
                else:
                    if path_obj.exists():
                        result = self.modify_file(
                            path,
                            changes
                        )
                    else:
                        result = self.create_file_from_changes(
                            path,
                            changes
                        )

            results.append(
                result
            )

        if not results:

            return {
                "success": False,
                "message": "No valid files were provided.",
                "results": []
            }

        success = all(
            isinstance(result, dict)
            and result.get("status") in {
                "updated",
                "created",
            }
            and "error" not in result
            for result in results
        )

        if not success:
            for snapshot_path, original_content in snapshots.items():
                rollback_result = self.atomic_writer.restore(
                    snapshot_path,
                    original_content
                )

                if not rollback_result.get(
                    "success",
                    False
                ):
                    self.logger.error(
                        "Code writer rollback failed for "
                        f"{snapshot_path}: "
                        f"{rollback_result.get('error')}"
                    )

        return {
            "success": success,
            "results": results,
            "files_written": [
                result["file"]
                for result in results
                if (
                    isinstance(result, dict)
                    and result.get("status") in {
                        "updated",
                        "created"
                    }
                )
            ]
        }

    def create_file(
        self,
        filename,
        code
    ):
        if not self.workspace:

            return {
                "file": filename,
                "error": "Workspace is not configured."
            }

        workspace_path = Path(
            self.workspace
        ).resolve()

        path = (
            workspace_path
            / filename
        ).resolve()

        # ---------------------------------------------------------
        # Workspace security
        # ---------------------------------------------------------

        try:

            path.relative_to(
                workspace_path
            )

        except ValueError:

            self.logger.error(
                f"Blocked path outside workspace: {filename}"
            )

            return {
                "file": filename,
                "error": "Path is outside the workspace."
            }

        if path.exists():

            return {
                "file": filename,
                "error": "File already exists."
            }

        if not code.strip():

            return {
                "file": filename,
                "error": "Generated code is empty."
            }

        # ---------------------------------------------------------
        # Syntax validation
        # ---------------------------------------------------------

        syntax_error = self.validate_python(
            code,
            filename
        )

        if syntax_error is not None:

            return {
                "file": filename,
                "error": (
                    "Generated code has invalid Python syntax."
                ),
                "details": syntax_error
            }

        # ---------------------------------------------------------
        # Formatting
        # ---------------------------------------------------------

        formatted = self.format_code(
            code
        )

        if formatted is not None:

            code = formatted

        # ---------------------------------------------------------
        # Final syntax validation
        # ---------------------------------------------------------

        syntax_error = self.validate_python(
            code,
            filename
        )

        if syntax_error is not None:

            return {
                "file": filename,
                "error": (
                    "Formatted code failed Python "
                    "syntax validation."
                ),
                "details": syntax_error
            }

        # ---------------------------------------------------------
        # Atomic write
        # ---------------------------------------------------------

        if self.atomic_writer is None:

            return {
                "file": filename,
                "error": "Atomic writer is not configured."
            }

        write_result = self.atomic_writer.write(
            path,
            code
        )

        if not write_result.get(
            "success",
            False
        ):

            return {
                "file": filename,
                "error": "Atomic write failed.",
                "details": write_result.get(
                    "error"
                )
            }

        # ---------------------------------------------------------
        # Verify written file
        # ---------------------------------------------------------

        try:

            written_code = path.read_text(
                encoding="utf-8"
            )

        except Exception as error:

            return {
                "file": filename,
                "error": (
                    f"Failed to verify written file: {error}"
                )
            }

        verification_error = self.validate_python(
            written_code,
            filename
        )

        if verification_error is not None:

            return {
                "file": filename,
                "error": (
                    "Written file failed Python "
                    "syntax verification."
                ),
                "details": verification_error
            }

        self.logger.info(
            f"Code file created and verified: {path}"
        )

        return {
            "file": filename,
            "status": "created"
        }

    def create_file_from_changes(
        self,
        filename,
        changes
    ):

        if not self.workspace:

            return {
                "file": filename,
                "error": "Workspace is not configured."
            }

        prompt = f"""
You are creating a NEW Python file inside an existing project.

This is a file creation task.

You must create ONLY the requested file.

==================================================
FILE
==================================================

{filename}

==================================================
REQUIRED CHANGES
==================================================

{changes}

==================================================
DEVELOPMENT CONTEXT
==================================================

{self.current_development_context}

==================================================
RULES
==================================================

- Create only the requested file.
- Do not modify existing files.
- Do not invent unrelated functionality.
- Do not introduce unnecessary dependencies.
- Follow the existing project architecture.
- Implement exactly the requested functionality.
- Keep the implementation minimal.
- The resulting code must be valid Python.

==================================================
OUTPUT RULES
==================================================

Return ONLY the complete Python source code.

Do NOT use Markdown.

Do NOT use code fences.

Do NOT include explanations.

Do NOT include text before the Python source.

Do NOT include text after the Python source.
"""

        try:

            code = self.llm.generate(
                prompt
            )

        except Exception as error:

            self.logger.error(
                f"Code generation exception for new file "
                f"{filename}: {error}"
            )

            return {
                "file": filename,
                "error": f"Code generation failed: {error}"
            }

        if isinstance(code, dict):

            return {
                "file": filename,
                "error": code
            }

        if not isinstance(code, str):

            return {
                "file": filename,
                "error": "LLM returned an invalid response type."
            }

        code = self.clean_code(
            code
        )

        if not code.strip():

            return {
                "file": filename,
                "error": "LLM returned empty code."
            }

        return self.create_file(
            filename,
            code
        )

    def modify_file(
        self,
        filename,
        changes
    ):

        if not self.workspace:

            return {
                "file": filename,
                "error": "Workspace is not configured."
            }

        workspace_path = Path(
            self.workspace
        ).resolve()

        path = (
            workspace_path
            / filename
        ).resolve()

        # ---------------------------------------------------------
        # Workspace security
        # ---------------------------------------------------------

        try:

            path.relative_to(
                workspace_path
            )

        except ValueError:

            self.logger.error(
                f"Blocked path outside workspace: {filename}"
            )

            return {
                "file": filename,
                "error": "Path is outside the workspace."
            }

        if not path.exists():

            return {
                "file": filename,
                "error": "File not found."
            }

        if not path.is_file():

            return {
                "file": filename,
                "error": "Target is not a file."
            }

        # ---------------------------------------------------------
        # Read original source
        # ---------------------------------------------------------

        try:

            old_code = path.read_text(
                encoding="utf-8"
            )

        except Exception as error:

            self.logger.error(
                f"Failed to read {filename}: {error}"
            )

            return {
                "file": filename,
                "error": f"Failed to read file: {error}"
            }

        # ---------------------------------------------------------
        # Capture architecture before modification
        # ---------------------------------------------------------

        original_structure = (
            self.extract_structure(
                old_code
            )
        )

        # ---------------------------------------------------------
        # Generate code
        # ---------------------------------------------------------

        prompt = f"""
You are modifying an EXISTING Python project.

This is NOT a greenfield task.

You must modify ONLY the requested file.

File:

{filename}

==================================================
CURRENT SOURCE CODE
==================================================

{old_code}

==================================================
REQUIRED CHANGES
==================================================

{changes}

==================================================
DEVELOPMENT CONTEXT
==================================================

{self.current_development_context}

==================================================
CRITICAL ARCHITECTURE RULES
==================================================

- Preserve the existing architecture.
- Preserve the existing class hierarchy.
- Preserve the existing public API.
- Preserve the existing constructor signature.
- Preserve existing public methods.
- Preserve existing dependencies.
- Do not redesign the class.
- Do not replace the implementation with another architecture.
- Do not introduce unrelated abstractions.
- Do not invent new managers, providers, registries or agents.
- Do not invent new files.
- Do not add dependencies unless explicitly required.
- Do not remove existing functionality.
- Do not rename existing public classes.
- Do not rename existing public methods.
- Do not change constructor parameters unless explicitly required.
- Make the smallest possible modification.
- If the requested change can be implemented with a small change,
  do NOT rewrite the entire file.
- Existing callers must remain compatible with the modified file.

==================================================
OUTPUT RULES
==================================================

Return ONLY the complete Python source code.

Do NOT use Markdown.

Do NOT use code fences.

Do NOT include explanations.

Do NOT include comments outside the Python source.

The resulting code MUST be valid Python.
"""

        try:

            new_code = self.llm.generate(
                prompt
            )

        except Exception as error:

            self.logger.error(
                f"Code generation exception for {filename}: {error}"
            )

            return {
                "file": filename,
                "error": f"Code generation failed: {error}"
            }

        if isinstance(new_code, dict):

            self.logger.error(
                f"Code generation failed for {filename}: {new_code}"
            )

            return {
                "file": filename,
                "error": new_code
            }

        if not isinstance(new_code, str):

            return {
                "file": filename,
                "error": (
                    "LLM returned an invalid response type."
                )
            }

        new_code = self.clean_code(
            new_code
        )

        if not new_code.strip():

            return {
                "file": filename,
                "error": "LLM returned empty code."
            }

        # ---------------------------------------------------------
        # First syntax validation
        # ---------------------------------------------------------

        syntax_error = self.validate_python(
            new_code,
            filename
        )

        if syntax_error is not None:

            self.logger.warning(
                f"Generated code has invalid Python syntax "
                f"for {filename}: {syntax_error}"
            )

            repaired = self.repair_code(
                filename,
                new_code
            )

            if repaired is None:

                return {
                    "file": filename,
                    "error": (
                        "Generated code has invalid Python syntax "
                        "and automatic repair failed."
                    ),
                    "details": syntax_error
                }

            new_code = repaired

        # ---------------------------------------------------------
        # Detect unchanged source
        # ---------------------------------------------------------

        if new_code.strip() == old_code.strip():

            self.logger.warning(
                f"Generated code is identical to the existing "
                f"file: {filename}"
            )

            return {
                "file": filename,
                "error": (
                    "Generated code is identical to the "
                    "existing file."
                )
            }       

        # ---------------------------------------------------------
        # Reject semantically unchanged code
        # ---------------------------------------------------------

        semantic_error = self.validate_semantic_change(
            old_code,
            new_code
        )

        if semantic_error is not None:

            self.logger.warning(
                f"{semantic_error}: {filename}"
            )

            return {
                "file": filename,
                "error": semantic_error
            } 

        # ---------------------------------------------------------
        # Architecture validation
        # ---------------------------------------------------------

        architecture_error = (
            self.validate_architecture(
                original_structure,
                new_code,
                filename
            )
        )

        if architecture_error is not None:

            self.logger.warning(
                f"Architecture validation failed for "
                f"{filename}: {architecture_error}"
            )

            repaired = self.repair_code(
                filename,
                new_code,
                architecture_error
            )

            if repaired is None:

                if (
                    architecture_error.startswith(
                        "Public method "
                    )
                    or
                    architecture_error.startswith(
                        "Constructor signature "
                    )
                ):

                    return {
                        "file": filename,
                        "error": architecture_error
                    }

                return {
                    "file": filename,
                    "error": (
                        "Generated code violates the existing "
                        "architecture."
                    ),
                    "details": architecture_error
                }

            new_code = repaired

            architecture_error = (
                self.validate_architecture(
                    original_structure,
                    new_code,
                    filename
                )
            )

            if architecture_error is not None:

                return {
                    "file": filename,
                    "error": (
                        "Code repair completed, but the resulting "
                        "code still violates the existing architecture."
                    ),
                    "details": architecture_error
                }

        # ---------------------------------------------------------
        # Requested change validation
        # ---------------------------------------------------------

        requested_change_error = (
            self.validate_requested_changes(
                changes,
                old_code,
                new_code
            )
        )

        if requested_change_error is not None:

            self.logger.warning(
                f"Requested change validation failed for "
                f"{filename}: {requested_change_error}"
            )

            return {
                "file": filename,
                "error": requested_change_error
            }

        # ---------------------------------------------------------
        # Final syntax validation
        # ---------------------------------------------------------

        syntax_error = self.validate_python(
            new_code,
            filename
        )

        if syntax_error is not None:

            return {
                "file": filename,
                "error": (
                    "Final generated code failed Python "
                    "syntax validation."
                ),
                "details": syntax_error
            }

        # ---------------------------------------------------------
        # Final formatting
        # ---------------------------------------------------------

        formatted = self.format_code(
            new_code
        )

        if formatted is not None:

            new_code = formatted

        # ---------------------------------------------------------
        # Final validation after formatting
        # ---------------------------------------------------------

        syntax_error = self.validate_python(
            new_code,
            filename
        )

        if syntax_error is not None:

            return {
                "file": filename,
                "error": (
                    "Formatted code failed Python "
                    "syntax validation."
                ),
                "details": syntax_error
            }

        architecture_error = (
            self.validate_architecture(
                original_structure,
                new_code,
                filename
            )
        )

        if architecture_error is not None:

            return {
                "file": filename,
                "error": (
                    "Formatted code violates the existing "
                    "architecture."
                ),
                "details": architecture_error
            }

        # ---------------------------------------------------------
        # Atomic Write
        # ---------------------------------------------------------

        if self.atomic_writer is None:

            return {
                "file": filename,
                "error": "Atomic writer is not configured."
            }

        write_result = self.atomic_writer.write(
            path,
            new_code
        )

        if not write_result.get(
            "success",
            False
        ):

            return {
                "file": filename,
                "error": (
                    "Atomic write failed."
                ),
                "details": write_result.get(
                    "error"
                )
            }

        # ---------------------------------------------------------
        # Verify written file
        # ---------------------------------------------------------

        try:

            written_code = path.read_text(
                encoding="utf-8"
            )

        except Exception as error:

            return {
                "file": filename,
                "error": (
                    f"Failed to verify written file: {error}"
                )
            }

        verification_error = (
            self.validate_python(
                written_code,
                filename
            )
        )

        if verification_error is not None:

            return {
                "file": filename,
                "error": (
                    "Written file failed Python syntax verification."
                ),
                "details": verification_error
            }

        architecture_error = (
            self.validate_architecture(
                original_structure,
                written_code,
                filename
            )
        )

        if architecture_error is not None:

            return {
                "file": filename,
                "error": (
                    "Written file failed architecture verification."
                ),
                "details": architecture_error
            }

        self.logger.info(
            f"Code updated and verified: {path}"
        )

        return {
            "file": filename,
            "status": "updated"
        }

    # =============================================================
    # Architecture analysis
    # =============================================================

    def extract_structure(
        self,
        code
    ):

        try:

            tree = ast.parse(
                code
            )

        except SyntaxError:

            return {
                "classes": {},
                "functions": [],
                "imports": []
            }

        classes = {}

        functions = []

        imports = []

        for node in tree.body:

            if isinstance(
                node,
                ast.ClassDef
            ):

                bases = []

                for base in node.bases:

                    try:

                        bases.append(
                            ast.unparse(base)
                        )

                    except Exception:

                        bases.append(
                            "<unknown>"
                        )

                methods = {}

                for child in node.body:

                    if isinstance(
                        child,
                        (
                            ast.FunctionDef,
                            ast.AsyncFunctionDef
                        )
                    ):

                        methods[child.name] = {
                            "signature": self.extract_signature(
                            child
                            ),
                            "async": isinstance(
                                child,
                                ast.AsyncFunctionDef
                            )
                        }

                classes[node.name] = {
                    "bases": bases,
                    "methods": methods
                }

            elif isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef
                )
            ):

                functions.append(
                    node.name
                )

            elif isinstance(
                node,
                ast.Import
            ):

                for alias in node.names:
                    imports.append({
                        "module": alias.name,
                        "name": None,
                        "kind": "import",
                    })

            elif isinstance(
                node,
                ast.ImportFrom
            ):
                module = node.module or ""

                for alias in node.names:
                    imports.append({
                        "module": module,
                        "name": alias.name,
                        "kind": "from",
                    })

        return {
            "classes": classes,
            "functions": functions,
            "imports": imports
        }

    def extract_signature(
        self,
        node
    ):

        try:

            return ast.unparse(
                node.args
            )

        except Exception:

            return "<unknown>"

    def validate_architecture(
        self,
        original,
        new_code,
        filename
    ):

        try:

            new_structure = (
                self.extract_structure(
                    new_code
                )
            )

        except Exception as error:

            return str(error)

        original_classes = (
            original.get(
                "classes",
                {}
            )
        )

        new_classes = (
            new_structure.get(
                "classes",
                {}
            )
        )

        # ---------------------------------------------------------
        # Existing classes must remain
        # ---------------------------------------------------------

        for class_name, class_info in original_classes.items():

            if class_name not in new_classes:

                return (
                    f"Existing class '{class_name}' "
                    f"was removed."
                )

            original_bases = set(
                class_info.get(
                    "bases",
                    []
                )
            )

            new_bases = set(
                new_classes[class_name].get(
                    "bases",
                    []
                )
            )

            if original_bases != new_bases:

                return (
                    f"Class '{class_name}' inheritance changed. "
                    f"Expected {sorted(original_bases)}, "
                    f"got {sorted(new_bases)}."
                )

            original_methods = class_info.get(
                    "methods",
                    {}
            )

            new_methods = new_classes[class_name].get(
                    "methods",
                    {}
            )

            missing_methods = (
                set(original_methods)
                -
                set(new_methods)
            )

            if missing_methods:

                return (
                    f"Class '{class_name}' lost existing "
                    f"methods: "
                    f"{sorted(missing_methods)}."
                )

            for method_name, method_info in original_methods.items():

                new_method_info = new_methods.get(
                    method_name
                )

                if new_method_info is None:
                    continue

                if (
                    method_info.get("signature")
                    !=
                    new_method_info.get("signature")
                    or
                    method_info.get("async")
                    !=
                    new_method_info.get("async")
                ):

                    if method_name == "__init__":

                        return (
                            f"Constructor signature for "
                            f"'{class_name}' changed."
                        )

                    if not method_name.startswith("_"):

                        return (
                            f"Public method "
                            f"'{class_name}.{method_name}' "
                            f"signature changed."
                        )                        

        # ---------------------------------------------------------
        # Existing top-level functions must remain
        # ---------------------------------------------------------

        original_functions = set(
            original.get(
                "functions",
                []
            )
        )

        new_functions = set(
            new_structure.get(
                "functions",
                []
            )
        )

        missing_functions = (
            original_functions
            -
            new_functions
        )

        if missing_functions:

            return (
                "Existing top-level functions were removed: "
                f"{sorted(missing_functions)}."
            )

        # ---------------------------------------------------------
        # Existing dependencies must remain
        # ---------------------------------------------------------
        #
        # Import syntax itself is not part of the architecture.
        #
        # These two forms can represent the same dependency:
        #
        #     from calculator import add
        #
        #     import calculator
        #
        # What matters is that the imported module/dependency has
        # not disappeared completely.
        # ---------------------------------------------------------

        original_imports = original.get(
            "imports",
            []
        )

        new_imports = new_structure.get(
            "imports",
            []
        )

        def import_modules(imports):
            modules = set()

            for item in imports:

                if isinstance(item, dict):

                    module = item.get(
                        "module"
                    )

                    if module:
                        modules.add(
                            str(module).lower()
                        )

                elif isinstance(item, str):

                    # Backward compatibility with older
                    # structure representations.
                    try:

                        tree = ast.parse(
                            item
                        )

                        for node in tree.body:

                            if isinstance(
                                node,
                                ast.Import
                            ):

                                for alias in node.names:
                                    modules.add(
                                        alias.name.lower()
                                    )

                            elif isinstance(
                                node,
                                ast.ImportFrom
                            ):

                                if node.module:
                                    modules.add(
                                        node.module.lower()
                                    )

                    except Exception:
                        continue

            return modules

        original_modules = import_modules(
            original_imports
        )

        new_modules = import_modules(
            new_imports
        )

        missing_dependencies = (
            original_modules
            -
            new_modules
        )

        if missing_dependencies:

            removed_imports = [
                f"import {module}"
                for module in sorted(
                    missing_dependencies
                )
            ]

            return (
                "Existing imports were removed: "
                f"{removed_imports}."
            )

        return None

    # =============================================================
    # Code repair
    # =============================================================

    def repair_code(
        self,
        filename,
        code,
        reason=None
    ):

        if not self.registry:

            self.logger.error(
                "Tool registry unavailable; "
                "cannot perform automatic code repair."
            )

            return None

        repair_tool = self.registry.get(
            "code_repair"
        )

        if repair_tool is None:

            self.logger.error(
                "Code repair tool is not registered."
            )

            return None

        try:

            result = repair_tool.execute({

                "filename": filename,

                "code": code,

                "context": (
                    reason
                    or
                    "Repair the generated Python code."
                )

            })

        except Exception as error:

            self.logger.error(
                f"Code repair failed for {filename}: {error}"
            )

            return None

        if not isinstance(result, dict):

            return None

        if not result.get(
            "success",
            False
        ):

            self.logger.error(
                f"Code repair returned failure for "
                f"{filename}: {result}"
            )

            return None

        repaired_code = result.get(
            "code"
        )

        if not isinstance(
            repaired_code,
            str
        ):

            self.logger.error(
                f"Code repair returned invalid code "
                f"for {filename}"
            )

            return None

        repaired_code = self.clean_code(
            repaired_code
        )

        if not repaired_code.strip():

            return None

        return repaired_code

    # =============================================================
    # Formatter
    # =============================================================

    def format_code(
        self,
        code
    ):

        try:

            tree = ast.parse(
                code
            )

            return (
                ast.unparse(
                    tree
                ).strip()
                + "\n"
            )

        except Exception as error:

            self.logger.warning(
                f"Formatting skipped: {error}"
            )

            return None

    # =============================================================
    # Semantic change validation
    # =============================================================

    def validate_semantic_change(
        self,
        old_code,
        new_code
    ):

        try:

            old_tree = ast.parse(
                old_code
            )

            new_tree = ast.parse(
                new_code
            )

            old_normalized = ast.dump(
                old_tree,
                annotate_fields=True,
                include_attributes=False
            )

            new_normalized = ast.dump(
                new_tree,
                annotate_fields=True,
                include_attributes=False
            )

            if old_normalized == new_normalized:

                return (
                    "Generated code is semantically identical "
                    "to the existing file."
                )

        except Exception as error:

            self.logger.warning(
                f"Semantic comparison skipped: {error}"
            )

        return None

    # =============================================================
    # Requested change validation
    # =============================================================
    def validate_requested_changes(
        self,
        changes,
        old_code,
        new_code
    ):
        """
        Validate explicitly structured requested changes.

        Legacy string-based changes remain unsupported by this
        validator and continue through the existing pipeline.

        Verification expressions are evaluated through a restricted
        AST evaluator. Function calls, attribute access, subscripts,
        assignments, imports, and other executable constructs are
        rejected.
        """

        if not isinstance(changes, list):
            return None

        structured_changes = [
            change
            for change in changes
            if isinstance(change, dict)
            and change.get("verification")
        ]

        if not structured_changes:
            return None

        for change in structured_changes:

            verification = change.get(
                "verification"
            )

            if not isinstance(
                verification,
                str
            ):
                continue

            verification = verification.strip()

            if not verification:
                continue

            try:

                tree = ast.parse(
                    verification,
                    mode="eval"
                )

                result = self._evaluate_verification(
                    tree.body,
                    old_code,
                    new_code
                )

            except Exception as error:

                return (
                    "Requested change verification failed: "
                    f"{error}"
                )

            if result is not True:

                description = change.get(
                    "description",
                    "Requested change"
                )

                return (
                    "Requested change was not satisfied: "
                    f"{description}"
                )

        return None


    def _evaluate_verification(
        self,
        node,
        old_code,
        new_code
    ):
        """
        Evaluate the restricted verification expression language.

        Supported:
        - old_code / new_code
        - string literals
        - == / !=
        - in / not in
        - and / or
        - not
        - parentheses

        Function calls, attribute access, subscripts and all other
        expression types are rejected.
        """

        if isinstance(
            node,
            ast.Constant
        ):

            if isinstance(
                node.value,
                str
            ):

                return node.value

            if isinstance(
                node.value,
                bool
            ):

                return node.value

            raise ValueError(
                "Only string and boolean literals are allowed."
            )

        if isinstance(
            node,
            ast.Name
        ):

            if node.id == "old_code":
                return old_code

            if node.id == "new_code":
                return new_code

            raise ValueError(
                f"Unsupported verification variable: {node.id}"
            )

        if isinstance(
            node,
            ast.BoolOp
        ):

            values = [
                self._evaluate_verification(
                    value,
                    old_code,
                    new_code
                )
                for value in node.values
            ]

            if isinstance(
                node.op,
                ast.And
            ):

                return all(values)

            if isinstance(
                node.op,
                ast.Or
            ):

                return any(values)

            raise ValueError(
                "Unsupported boolean operator."
            )

        if isinstance(
            node,
            ast.UnaryOp
        ):

            if not isinstance(
                node.op,
                ast.Not
            ):

                raise ValueError(
                    "Only 'not' is supported."
                )

            return not self._evaluate_verification(
                node.operand,
                old_code,
                new_code
            )

        if isinstance(
            node,
            ast.Compare
        ):

            left = self._evaluate_verification(
                node.left,
                old_code,
                new_code
            )

            for operator, comparator_node in zip(
                node.ops,
                node.comparators
            ):

                right = self._evaluate_verification(
                    comparator_node,
                    old_code,
                    new_code
                )

                if isinstance(
                    operator,
                    ast.Eq
                ):

                    comparison = (
                        left == right
                    )

                elif isinstance(
                    operator,
                    ast.NotEq
                ):

                    comparison = (
                        left != right
                    )

                elif isinstance(
                    operator,
                    ast.In
                ):

                    comparison = (
                        left in right
                    )

                elif isinstance(
                    operator,
                    ast.NotIn
                ):

                    comparison = (
                        left not in right
                    )

                else:

                    raise ValueError(
                        "Unsupported comparison operator."
                    )

                if not comparison:
                    return False

                left = right

            return True

        raise ValueError(
            "Unsupported verification expression."
        )

    # =============================================================
    # Syntax validation
    # =============================================================

    def validate_python(
        self,
        code,
        filename="<unknown>"
    ):

        try:

            ast.parse(
                code,
                filename=filename
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

    # =============================================================
    # Code cleanup
    # =============================================================

    def clean_code(
        self,
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

        if code.startswith(
            "```"
        ):

            lines = code.splitlines()

            if lines:

                if lines[0].strip().startswith(
                    "```"
                ):

                    lines = lines[1:]

            if lines and lines[-1].strip() == "```":

                lines = lines[:-1]

            code = "\n".join(
                lines
            )

        return code.strip() + "\n"