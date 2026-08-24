"""Python-specific structural analysis for repository files."""

import ast
from pathlib import Path


class PythonAnalyzer:
    """Extract Python symbols and import facts without owning repository scanning."""

    def analyze_file(self, path, root=None):
        path = Path(path)
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeError):
            return {"symbols": [], "dependencies": [], "definitions": []}
        relative = path.relative_to(root).as_posix() if root else path.as_posix()
        try:
            tree = ast.parse(source)
        except (SyntaxError, ValueError):
            return {"symbols": [], "dependencies": [], "definitions": []}

        symbols = []
        definitions = []
        dependencies = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                definitions.append(f"def {node.name}(")
                symbols.append(self._symbol(relative, node.name, "function", node))
            elif isinstance(node, ast.ClassDef):
                methods = [
                    item.name
                    for item in node.body
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]
                suffix = ", ".join(methods[:5])
                definitions.append(f"class {node.name}({suffix})")
                symbols.append(self._symbol(relative, node.name, "class", node))
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        symbols.append(
                            self._symbol(
                                relative,
                                f"{node.name}.{item.name}",
                                "method",
                                item,
                                node.name,
                            )
                        )

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                dependencies.extend(
                    self._dependency(relative, alias.name) for alias in node.names
                )
            elif isinstance(node, ast.ImportFrom):
                dependencies.append(
                    self._dependency(relative, node.module or "", "import_from")
                )

        symbols.sort(key=lambda item: (item.get("line") or 0, item["id"]))
        dependencies.sort(key=lambda item: (item["target"], item["kind"]))

        return {
            "symbols": symbols,
            "dependencies": dependencies,
            "definitions": definitions,
        }

    @staticmethod
    def _symbol(path, name, kind, node, parent=None):
        result = {
            "id": f"{path}::{name}",
            "name": name,
            "kind": kind,
            "language": "python",
            "line": getattr(node, "lineno", None),
            "end_line": getattr(node, "end_lineno", None),
        }
        if parent:
            result["parent"] = parent
        return result

    @staticmethod
    def _dependency(source, target, kind="import"):
        return {
            "source": source,
            "target": target,
            "kind": kind,
            "language": "python",
        }
