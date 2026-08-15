from agents.code_agent import CodeAgent
from agents.planner_agent import PlannerAgent

from app.core.orchestrators.development_orchestrator import DevelopmentOrchestrator
from app.core.workspace.watcher import WorkspaceWatcher


class DevelopmentContainer:

    def __init__(
        self,
        main
    ):

        #
        # Shared systems
        #

        self.project_memory = (
            main.memory.project_memory
        )

        self.workspace_path = (
            main.core.workspace_path
        )



        #
        # Tool Registry
        #

        self.registry = (
            main.tools.registry
        )



        #
        # LLMs
        #

        self.code_llm = (
            main.models.code_llm
        )

        self.planner_llm = (
            main.models.planner_llm
        )



        #
        # Agents
        #

        self.planner = PlannerAgent(
            self.planner_llm,
            main.memory.memory,
            self.registry
        )


        self.code_agent = CodeAgent(
            self.code_llm,
            self.registry,
            main.memory.memory,
            self.workspace_path
        )



        #
        # Repository Analyzer
        #

        self.repository_analyzer = (
            self.registry.get(
                "repository_analyzer"
            )
        )



        #
        # Workspace Watcher
        #

        self.watcher = WorkspaceWatcher(
            self.workspace_path,
            self.on_workspace_changes
        )

        self.watcher.start()



        #
        # Future
        #

        self.improvement_agent = None



        #
        # Orchestrator
        #

        self.orchestrator = DevelopmentOrchestrator(
            self
        )



    def on_workspace_changes(
        self,
        changed_files
    ):

        self.project_memory.update_project_info(
            {
                "changed_files": changed_files
            }
        )