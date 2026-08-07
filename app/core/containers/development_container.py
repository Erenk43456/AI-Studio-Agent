from agents.code_agent import CodeAgent
from agents.planner_agent import PlannerAgent

from app.core.orchestrators.development_orchestrator import DevelopmentOrchestrator


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
            self.planner_llm
        )


        self.code_agent = CodeAgent(
            self.code_llm,
            self.registry,
            main.memory.memory,
            main.core.workspace_path
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
        # Future
        #

        self.improvement_agent = None


        #
        # Orchestrator
        #

        self.orchestrator = DevelopmentOrchestrator(
            self
        )