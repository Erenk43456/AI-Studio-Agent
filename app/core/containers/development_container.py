from agents.planner_agent import PlannerAgent
from agents.tool_agent import ToolAgent

from app.core.development_context import DevelopmentContext

from app.core.orchestrators.development_orchestrator import DevelopmentOrchestrator

from app.core.workspace.watcher import WorkspaceWatcher
from app.core.project_memory_sync import ProjectMemorySync


class DevelopmentContainer:

    def __init__(self, main):

        #
        # Shared systems
        #

        self.project_memory = main.memory.project_memory

        self.workspace_path = main.core.workspace_path

        #
        # Tool Registry
        #

        self.registry = main.tools.registry

        #
        # LLMs
        #

        self.code_llm = main.models.code_llm

        self.planner_llm = main.models.planner_llm

        #
        # Development Context
        #

        self.development_context = DevelopmentContext(
            self.project_memory, self.workspace_path
        )

        #
        # Agents
        #

        self.planner = PlannerAgent(self.planner_llm, registry=self.registry)

        self.code_agent = main.agents.code

        self.code_agent.development_context = self.development_context

        self.tool_agent = ToolAgent(
            registry=self.registry,
            memory=main.memory.memory,
            llm=self.code_llm,
            code_agent=self.code_agent,
        )

        #
        # Repository Analyzer
        #

        self.repository_analyzer = self.registry.get("repository_analyzer")

        #
        # Project Memory Sync
        #
        self.project_memory_sync = ProjectMemorySync(
            repository_analyzer=self.repository_analyzer,
            project_memory=self.project_memory,
            workspace=self.workspace_path,
        )

        initialize = getattr(
            self.project_memory_sync,
            "initialize",
            None,
        )

        if initialize:
            initialize()

        #
        # Workspace Watcher
        #

        self.watcher = WorkspaceWatcher(self.workspace_path, self.on_workspace_changes)

        self.watcher.start()

        #
        # Future
        #

        self.improvement_agent = None

        #
        # Orchestrator
        #

        self.orchestrator = DevelopmentOrchestrator(self)

    def on_workspace_changes(self, changed_files):

        self.project_memory_sync.sync(changed_files)

    def close(self):
        if self.watcher:
            self.watcher.stop()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()