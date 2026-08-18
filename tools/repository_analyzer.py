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
    # Core
    "app/core/containers/core_container.py":
        "Core dependency and workspace configuration",

    "app/core/containers/model_container.py":
        "Creates and configures LLM providers",

    "app/core/containers/memory_container.py":
        "Creates persistent memory, conversation memory, chat manager, and project memory",

    "app/core/containers/tool_container.py":
        "Creates and registers all executable tools",

    "app/core/containers/agent_container.py":
        "Creates and wires application agents",

    "app/core/containers/chat_container.py":
        "Creates ChatAgent and ChatOrchestrator",

    "app/core/containers/development_container.py":
        "Creates development agents, repository analyzer access, watcher, and DevelopmentOrchestrator",

    "app/core/containers/main_container.py":
        "Application dependency injection composition root",

    # Orchestration
    "app/core/orchestrators/main_orchestrator.py":
        "Routes requests between chat, memory, and development systems",

    "app/core/orchestrators/chat_orchestrator.py":
        "Routes chat requests to ChatAgent",

    "app/core/orchestrators/memory_orchestrator.py":
        "Routes memory operations to MemoryAgent",

    "app/core/orchestrators/development_orchestrator.py":
        "Plans and executes development tasks",

    # Agents
    "agents/planner_agent.py":
        "Creates structured execution plans",

    "agents/chat_agent.py":
        "Conversational agent building the LLM prompt",

    "agents/tool_agent.py":
        "Executes single tools and multi-step plans",

    "agents/code_agent.py":
        "Code-task agent",

    "agents/decision_agent.py":
        "Routes incoming user requests to the appropriate system",

    "agents/memory_agent.py":
        "Handles persistent user memory operations",

    # Models
    "models/llm_provider.py":
        "Selects local or API LLM backend",

    "models/llm.py":
        "Ollama local LLM client",

    "models/api_llm.py":
        "OpenAI-compatible API LLM client",

    # Memory
    "memory/memory.py":
        "Persistent key-value user memory",

    "memory/conversation.py":
        "Per-conversation rolling history",

    "memory/chat_manager.py":
        "Chat session management",

    # Tools
    "tools/tool_registry.py":
        "Tool name to implementation registry",

    "tools/repository_analyzer.py":
        "Static repository architecture analyzer",

    "tools/project_memory_tool.py":
        "Project memory tool",

    "tools/memory_tool.py":
        "User memory tool",

    # Configuration / GUI
    "config/config_manager.py":
        "JSON configuration and environment settings",

    "app/window/backend.py":
        "Exposes application services to the GUI",

    "app/window/main_window.py":
        "Main Qt window and GUI wiring",

    "app/worker.py":
        "Background worker for AI requests",
}

# (label, relative file, ordered substrings) -> wiring check
CHECKS = [

    # --------------------------------------------------------------
    # Main Container
    # --------------------------------------------------------------

    (
        "MainContainer wires CoreContainer",
        "app/core/containers/main_container.py",
        ["self.core = CoreContainer("],
    ),

    (
        "MainContainer wires ModelContainer",
        "app/core/containers/main_container.py",
        ["self.models = ModelContainer("],
    ),

    (
        "MainContainer wires MemoryContainer",
        "app/core/containers/main_container.py",
        ["self.memory = MemoryContainer("],
    ),

    (
        "MainContainer wires ToolContainer",
        "app/core/containers/main_container.py",
        ["self.tools = ToolContainer("],
    ),

    (
        "MainContainer wires AgentContainer",
        "app/core/containers/main_container.py",
        ["self.agents = AgentContainer("],
    ),

    (
        "MainContainer wires ChatContainer",
        "app/core/containers/main_container.py",
        ["self.chat = ChatContainer("],
    ),

    (
        "MainContainer wires DevelopmentContainer",
        "app/core/containers/main_container.py",
        ["self.development = DevelopmentContainer("],
    ),

    (
        "MainContainer creates MemoryOrchestrator",
        "app/core/containers/main_container.py",
        [
            "MemoryOrchestrator(",
            "self.memory.orchestrator",
        ],
    ),


    # --------------------------------------------------------------
    # Tool Container
    # --------------------------------------------------------------

    (
        "ToolContainer registers repository_analyzer",
        "app/core/containers/tool_container.py",
        [
            '"repository_analyzer"',
            "self.repository_analyzer",
        ],
    ),

    (
        "ToolContainer registers project_memory",
        "app/core/containers/tool_container.py",
        [
            '"project_memory"',
            "self.project_memory",
        ],
    ),

    (
        "ToolContainer registers memory",
        "app/core/containers/tool_container.py",
        [
            '"memory"',
            "self.memory_tool",
        ],
    ),

    (
        "ToolContainer registers code_writer",
        "app/core/containers/tool_container.py",
        [
            '"code_writer"',
            "self.code_writer",
        ],
    ),

    (
        "ToolContainer registers code_analyzer",
        "app/core/containers/tool_container.py",
        [
            '"code_analyzer"',
            "self.code_analyzer",
        ],
    ),

    (
        "ToolContainer registers code_repair",
        "app/core/containers/tool_container.py",
        [
            '"code_repair"',
            "self.code_repair",
        ],
    ),


    # --------------------------------------------------------------
    # Agent Container
    # --------------------------------------------------------------

    (
        "AgentContainer wires DecisionAgent",
        "app/core/containers/agent_container.py",
        [
            "self.decision = DecisionAgent(",
            "main.models.decision_llm",
        ],
    ),

    (
        "AgentContainer wires ChatAgent",
        "app/core/containers/agent_container.py",
        [
            "self.chat = ChatAgent(",
            "main.models.chat_llm",
        ],
    ),

    (
        "AgentContainer wires CodeAgent",
        "app/core/containers/agent_container.py",
        [
            "self.code = CodeAgent(",
            "main.models.code_llm",
        ],
    ),

    (
        "AgentContainer wires MemoryAgent",
        "app/core/containers/agent_container.py",
        [
            "self.memory = MemoryAgent(",
        ],
    ),


    # --------------------------------------------------------------
    # Chat Container
    # --------------------------------------------------------------

    (
        "ChatContainer wires ChatAgent",
        "app/core/containers/chat_container.py",
        [
            "self.chat_agent = ChatAgent(",
            "llm=self.llm",
            "memory=self.memory",
        ],
    ),

    (
        "ChatContainer wires ChatOrchestrator",
        "app/core/containers/chat_container.py",
        [
            "self.orchestrator = ChatOrchestrator(",
        ],
    ),


    # --------------------------------------------------------------
    # Development Container
    # --------------------------------------------------------------

    (
        "DevelopmentContainer wires PlannerAgent",
        "app/core/containers/development_container.py",
        [
            "self.planner = PlannerAgent(",
            "self.planner_llm",
            "main.memory.memory",
            "self.registry",
        ],
    ),

    (
        "DevelopmentContainer wires CodeAgent",
        "app/core/containers/development_container.py",
        [
            "self.code_agent = CodeAgent(",
            "self.code_llm",
        ],
    ),

    (
        "DevelopmentContainer resolves repository_analyzer",
        "app/core/containers/development_container.py",
        [
            'self.registry.get(',
            '"repository_analyzer"',
        ],
    ),

    (
        "DevelopmentContainer wires DevelopmentOrchestrator",
        "app/core/containers/development_container.py",
        [
            "self.orchestrator = DevelopmentOrchestrator(",
        ],
    ),


    # --------------------------------------------------------------
    # Main Orchestrator
    # --------------------------------------------------------------

    (
        "MainOrchestrator routes chat",
        "app/core/orchestrators/main_orchestrator.py",
        [
            '"chat":',
            "container.chat.orchestrator",
        ],
    ),

    (
        "MainOrchestrator routes memory",
        "app/core/orchestrators/main_orchestrator.py",
        [
            '"memory":',
            "container.memory.orchestrator",
        ],
    ),

    (
        "MainOrchestrator routes development",
        "app/core/orchestrators/main_orchestrator.py",
        [
            '"development":',
            "container.development.orchestrator",
        ],
    ),


    # --------------------------------------------------------------
    # Chat Orchestrator
    # --------------------------------------------------------------

    (
        "ChatOrchestrator forwards conversation",
        "app/core/orchestrators/chat_orchestrator.py",
        [
            "self.chat_agent.conversation =",
        ],
    ),


    # --------------------------------------------------------------
    # Core capabilities
    # --------------------------------------------------------------

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
        "LLM Planner supports repository_analyzer",
        "agents/planner/llm_planner.py",
        [
            "repository_analyzer",
            '"analyze"',
        ],
    ),
]


class RepositoryAnalyzerTool:

    name = "repository_analyzer"

    description = (
        "Analyzes the AI-Studio-Agent codebase"
    )

    purpose = (
        "Analyze the repository structure, architecture, dependencies, tools, and known issues."
    )

    safe = True

    modifies_files = False

    requires_confirmation = False
    
    version = "1.0"



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

    def __init__(
        self,
        root=".",
        memory=None,
    ):

        self.root = root

        self.memory = memory

        self.logger = AppLogger()

    def execute(self, plan):
        try:

            action = plan.get(
                "action", 
                "analyze"
            )


            if action != "analyze":

                return "Unsupported repository action."

            
            root = Path(
                plan.get("path") 
                or self.root
            )


            result = self.analyze(
                root
            )


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
        container = root / "app/core/containers/tool_container.py"
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
