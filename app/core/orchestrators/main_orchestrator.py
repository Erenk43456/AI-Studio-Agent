from app.core.logger import AppLogger


class MainOrchestrator:

    def __init__(
        self,
        container
    ):

        self.container = container

        self.logger = AppLogger()

        self.decision_agent = (
            container.agents.decision
        )

        self.systems = {

            "chat":
            container.chat.orchestrator,

            "memory":
            container.memory.orchestrator,

            "development":
            container.development.orchestrator

        }

        self.last_execution = {
            "agents": {},
            "models": {},
        }

    def run(
        self,
        message,
        conversation=None
    ):

        self.logger.info(
            f"Main request: {message}"
        )

        self.last_execution = {
            "agents": {},
            "models": {},
        }

        #
        # Decision Agent
        #

        decision_model = (
            self.container.models.decision_llm
            .get_current_model()
        )

        try:

            decision = self.decision_agent.process(
                message
            )

            self.last_execution["agents"]["decision"] = {
                "status": "PASS",
                "model": decision_model,
                "result": decision,
            }

            self.last_execution["models"]["decision"] = (
                decision_model
            )

        except Exception as error:

            self.last_execution["agents"]["decision"] = {
                "status": "FAIL",
                "model": decision_model,
                "error": str(error),
            }

            self.last_execution["models"]["decision"] = (
                decision_model
            )

            raise

        print(
            "DECISION:",
            decision
        )

        system = decision.get(
            "system",
            "chat"
        )

        orchestrator = self.systems.get(
            system
        )

        if orchestrator is None:

            self.logger.error(
                f"Unknown system: {system}"
            )

            return {
                "error":
                f"Unknown system: {system}"
            }

        #
        # Pass execution trace to system
        #

        return orchestrator.run(
            message,
            decision,
            conversation,
            execution=self.last_execution
        )