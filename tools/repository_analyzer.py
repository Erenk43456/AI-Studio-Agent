"""Static analyzer for the AI-Studio-Agent repository.

Follows the existing tool convention: the class exposes execute(plan).
Analysis is collected into a structured RepositoryAnalysis (data
layer) and rendered to the human-readable text report by
RepositoryReportFormatter (presentation layer).
"""

import ast
import re
import tokenize
from datetime import datetime
from pathlib import Path

from app.core.logger import AppLogger

from tools.repository_analysis import RepositoryAnalysis
from tools.repository_report import RepositoryReportFormatter


SKIP_DIRS = {
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "build",
    "dist",
    "release",
    "exports",
    "logs",
    "data",
    ".pytest_cache",
    ".mypy_cache",
    ".vscode",
    ".idea",
    "node_modules",
    ".aider.tags.cache.v4",
}

IGNORED_FILES = {"__init__.py"}

# Files under tools/ that are not tool implementations themselves.
TOOL_LIST_EXCLUDES = {
    "__init__.py",
    "tool_registry.py",
    "base_tool.py",
    "repository_analysis.py",
    "repository_report.py",
}

# Analyzer implementation files that scan the codebase for markers;
# scanning them would only report their own detection logic.
MARKER_SCAN_EXCLUDES = {
    "tools/repository_analyzer.py",
}

MARKER_PATTERN = re.compile(r"\b(?:TODO|FIXME|XXX)\b")

MODULE_ROLES = {
    "app/core/container.py": "Dependency injection composition root",
    "app/core/orchestrator/orchestrator.py": "Routes plans to chat/tool agents",
    "agents/planner_agent.py": "Keyword parsers -> LLM JSON plan fallback",
    "agents/chat_agent.py": "Conversational agent building the LLM prompt",
    "agents/tool_agent.py": "Executes single tools and multi-step plans",
    "agents/code_agent.py": "Code-task agent (currently unused)",
    "agents/decision_agent.py": "Legacy rule-based router (tests only)",
    "models/llm_provider.py": "Selects local (Ollama) or API LLM backend",
    "models/llm.py": "Ollama local LLM client",
    "models/api_llm.py": "API (OpenAI-style) LLM client",
    "memory/memory.py": "Persistent key-value memory (data/memory.json)",
    "memory/conversation.py": "Per-chat rolling conversation history",
    "memory/chat_manager.py": "Chat session index (data/chats.json)",
    "tools/tool_registry.py": "name -> tool instance registry",
    "config/config_manager.py": "JSON settings store (config/settings.json)",
    "app/window/backend.py": "Exposes container services to the GUI",
    "app/window/main_window.py": "Main Qt window wiring controllers",
    "app/worker.py": "Background QThread for AI requests",
}

# (label, relative file, ordered substrings) -> wiring check
CHECKS = [
    (
        "Container wires PlannerAgent(llm, memory)",
        "app/core/container.py",
        ["self.planner = PlannerAgent(", "self.llm,", "self.memory"],
    ),
    (
        "Container wires ChatAgent(llm, memory)",
        "app/core/container.py",
        ["self.chat_agent = ChatAgent(", "self.llm,", "self.memory"],
    ),
    (
        "repository_analyzer registered in container",
        "app/core/container.py",
        ['"repository_analyzer"'],
    ),
    (
        "Memory aliases registered (memory_save/memory_get)",
        "app/core/container.py",
        ['"memory_save"', '"memory_get"'],
    ),
    (
        "ConversationMemory.get_last exists",
        "memory/conversation.py",
        ["def get_last("],
    ),
    (
        "ToolAgent.execute_steps exists",
        "agents/tool_agent.py",
        ["def execute_steps("],
    ),
    (
        "Orchestrator forwards conversation to chat agent",
        "app/core/orchestrator/orchestrator.py",
        ["agent.conversation = conversation"],
    ),
    (
        "Planner includes repository_analyzer parser",
        "agents/planner_agent.py",
        ["repository_analyzer", "parse_repository_analyzer"],
    ),
]


class RepositoryAnalyzerTool:
    """Analyzes the AI-Studio-Agent codebase.

    ``execute(plan)`` returns the human-readable text report (same
    contract as before). ``analyze(root)`` returns the structured
    RepositoryAnalysis for programmatic consumers.
    """

    name = "repository_analyzer"
    description = (
        "Analyzes the AI-Studio-Agent repository structure, architecture, "
        "agent flow, dependency injection, LLM provider, memory system, "
        "tool registry, GUI layout, and known issues."
    )

    def __init__(self, root="."):
        self.root = root
        self.logger = AppLogger()

    def execute(self, plan):
        try:
            action = plan.get("action", "analyze")
            if action != "analyze":
                return "Unsupported repository action."
            root = Path(plan.get("path") or self.root)
            result = self.analyze(root)
            if isinstance(result, str):
                return result
            return RepositoryReportFormatter.render(result)
        except Exception as error:
            self.logger.error(f"Repository analysis error: {error}")
            return f"Repository analysis error: {error}"

    # ------------------------------------------------------------------
    # public analysis entry point
    # ------------------------------------------------------------------

    def analyze(self, root):
        root = Path(root)
        if not root.exists():
            return f"Path not found: {root}"
        if not (root / "main.py").exists():
            return f"Not an AI-Studio-Agent repository root: {root}"

        tools, registry_names = self._collect_tools(root)

        return RepositoryAnalysis(
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            overview=self._collect_overview(root),
            module_roles=self._collect_module_roles(root),
            definitions=self._collect_definitions(root),
            tools=tools,
            registry_names=registry_names,
            wiring_checks=self._collect_wiring_checks(root),
            issues=self._collect_issues(root),
        )

    # ------------------------------------------------------------------
    # data collection (returns plain structures)
    # ------------------------------------------------------------------

    def _iter_python_files(self, root):
        for path in sorted(root.rglob("*.py")):
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            if path.name in IGNORED_FILES:
                continue
            yield path

    @staticmethod
    def _read(path):
        return path.read_text(encoding="utf-8", errors="replace")

    @staticmethod
    def _top_level_defs(source):
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return []
        defs = []
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                methods = [
                    n.name
                    for n in node.body
                    if isinstance(n, ast.FunctionDef)
                ]
                suffix = ", ".join(methods[:5])
                defs.append(f"class {node.name}({suffix})")
            elif isinstance(node, ast.FunctionDef):
                defs.append(f"def {node.name}(")
        return defs

    def _collect_overview(self, root):
        files = list(self._iter_python_files(root))
        total_lines = sum(
            len(self._read(path).splitlines())
            for path in files
        )
        biggest = sorted(
            files,
            key=lambda path: len(self._read(path).splitlines()),
            reverse=True,
        )[:5]
        return {
            "root": str(root.resolve()),
            "python_files": len(files),
            "total_lines": total_lines,
            "top_level_modules": sorted(
                path.name
                for path in root.iterdir()
                if path.is_dir() and path.name not in SKIP_DIRS
            ),
            "largest_files": [
                {
                    "file": path.as_posix(),
                    "lines": len(self._read(path).splitlines()),
                }
                for path in biggest
            ],
        }

    def _collect_module_roles(self, root):
        return {
            rel: role
            for rel, role in MODULE_ROLES.items()
            if (root / rel).exists()
        }

    def _collect_definitions(self, root):
        definitions = {}
        for rel in MODULE_ROLES:
            path = root / rel
            if not path.exists():
                continue
            defs = self._top_level_defs(self._read(path))
            if defs:
                definitions[rel] = defs
        return definitions

    def _collect_tools(self, root):
        tools = []
        tool_dir = root / "tools"
        if tool_dir.is_dir():
            for path in sorted(tool_dir.glob("*.py")):
                if path.name in TOOL_LIST_EXCLUDES:
                    continue
                tools.append(
                    {
                        "file": path.name,
                        "has_execute": bool(
                            re.search(r"def execute\(", self._read(path))
                        ),
                    }
                )
        container = root / "app/core/container.py"
        registry_names = []
        if container.exists():
            registry_names = re.findall(
                r'registry\.register\(\s*"([^"]+)"\s*,',
                self._read(container),
            )
        return tools, registry_names

    def _collect_wiring_checks(self, root):
        checks = []
        for label, rel, needles in CHECKS:
            path = root / rel
            if not path.exists():
                checks.append({"label": label, "ok": False})
                continue
            source = self._read(path)
            checks.append(
                {
                    "label": label,
                    "ok": all(needle in source for needle in needles),
                }
            )
        return checks

    def _collect_issues(self, root):
        issues = []
        for path in self._iter_python_files(root):
            rel = path.relative_to(root).as_posix()
            if rel in MARKER_SCAN_EXCLUDES:
                continue
            for number, line in self._iter_comment_lines(path):
                if MARKER_PATTERN.search(line):
                    issues.append(
                        {
                            "file": rel,
                            "line": number,
                            "message": line.strip()[:80],
                        }
                    )
        return issues

    def _iter_comment_lines(self, path):
        """Yield (line_number, content) for real comments only."""
        try:
            with path.open("rb") as file:
                tokens = tokenize.tokenize(file.readline)
                for token in tokens:
                    if token.type == tokenize.COMMENT:
                        yield token.start[0], token.line
        except (tokenize.TokenError, IndentationError, SyntaxError, OSError):
            return
