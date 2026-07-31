"""Static analyzer for the AI-Studio-Agent repository.

Follows the existing tool convention: classes expose execute(plan).
Performs offline (LLM-free) analysis of architecture, agent flow, DI,
LLM provider, memory, tool registry, GUI structure, and known issues.
"""

import ast
import re
import tokenize
from datetime import datetime
from pathlib import Path

from app.core.logger import AppLogger


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

# (label, relative file, ordered substrings) -> reported OK/FAIL
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
    """Analyzes the AI-Studio-Agent codebase and returns a text report."""

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
            return self.analyze(root)
        except Exception as error:
            self.logger.error(f"Repository analysis error: {error}")
            return f"Repository analysis error: {error}"

    # ------------------------------------------------------------------
    # helpers
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

    # ------------------------------------------------------------------
    # report sections
    # ------------------------------------------------------------------

    def _overview(self, root):
        files = list(self._iter_python_files(root))
        total_lines = sum(
            len(self._read(p).splitlines())
            for p in files
        )
        lines = [
            f"- Repository root: {root.resolve()}",
            f"- Python files: {len(files)}",
            f"- Total lines: {total_lines}",
            "- Top-level modules: "
            + ", ".join(p.name for p in sorted(root.iterdir()) if p.is_dir() and p.name not in SKIP_DIRS),
        ]
        biggest = sorted(
            files,
            key=lambda p: len(self._read(p).splitlines()),
            reverse=True,
        )[:5]
        lines.append(
            "- Largest files: "
            + ", ".join(f"{p} ({len(self._read(p).splitlines())} lines)" for p in biggest)
        )
        return "\n".join(lines)

    def _module_roles(self, root):
        found = []
        for rel, role in MODULE_ROLES.items():
            if (root / rel).exists():
                found.append(f"- {rel}\n    -> {role}")
        return "\n".join(found)

    def _definitions(self, root):
        sections = []
        for rel in MODULE_ROLES:
            path = root / rel
            if not path.exists():
                continue
            defs = self._top_level_defs(self._read(path))
            if defs:
                sections.append(f"- {rel}:")
                sections.append("    " + ", ".join(defs))
        return "\n".join(sections)

    def _tool_overview(self, root):
        tool_dir = root / "tools"
        if not tool_dir.is_dir():
            return "tools/ directory not found."
        lines = ["Registered tool implementations (tools/):"]
        for path in sorted(tool_dir.glob("*.py")):
            if path.name in {"__init__.py", "tool_registry.py", "base_tool.py"}:
                continue
            has_execute = bool(re.search(r"def execute\(", self._read(path)))
            status = "execute(): OK" if has_execute else "execute(): MISSING"
            lines.append(f"- {path.name}: {status}")
        container = self._read(root / "app/core/container.py")
        names = re.findall(
            r'registry\.register\(\s*"([^"]+)"\s*,',
            container,
        )
        lines.append(f"\nRegistered names in AIContainer: {', '.join(names)}")
        return "\n".join(lines)

    def _architecture_checks(self, root):
        lines = []
        for label, rel, needles in CHECKS:
            path = root / rel
            if not path.exists():
                lines.append(f"- [FAIL] {label} (missing file {rel})")
                continue
            source = self._read(path)
            ok = all(needle in source for needle in needles)
            lines.append(f"- [{'OK' if ok else 'FAIL'}] {label}")
        return "\n".join(lines)

    def _issues(self, root):
        markers = []
        for path in self._iter_python_files(root):
            rel = path.relative_to(root).as_posix()
            if rel in MARKER_SCAN_EXCLUDES:
                continue
            for number, line in self._iter_comment_lines(path):
                if MARKER_PATTERN.search(line):
                    markers.append(
                        f"- {rel}:{number}: {line.strip()[:80]}"
                    )
        return "\n".join(markers[:15]) if markers else "- No TODO/FIXME markers found."

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

    # ------------------------------------------------------------------
    # public
    # ------------------------------------------------------------------

    def analyze(self, root):
        if not root.exists():
            return f"Path not found: {root}"
        if not (root / "main.py").exists():
            return f"Not an AI-Studio-Agent repository root: {root}"

        report = [
            "=" * 60,
            "AI-Studio-Agent Repository Analysis",
            "=" * 60,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "[1] Overview",
            self._overview(root),
            "",
            "[2] Module Roles (architecture)",
            self._module_roles(root),
            "",
            "[3] Key Definitions",
            self._definitions(root),
            "",
            "[4] Tool Registry",
            self._tool_overview(root),
            "",
            "[5] Architecture & Wiring Checks",
            self._architecture_checks(root),
            "",
            "[6] TODO / FIXME Markers",
            self._issues(root),
            "",
            "=" * 60,
            "Analysis complete.",
            "=" * 60,
        ]
        return "\n".join(report)
