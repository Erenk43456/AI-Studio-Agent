from app.core.logger import AppLogger


class MainOrchestrator:


    def __init__(
        self,
        container
    ):


        self.container = container

        self.logger = AppLogger()



        #
        # Decision Agent
        #

        self.decision_agent = (
            container.agents.decision
        )



        #
        # Systems
        #

        self.systems = {

            "chat":
            container.chat.orchestrator,


            "memory":
            container.memory.orchestrator,


            "development":
            container.development.orchestrator

        }




    def run(
        self,
        message,
        conversation=None
    ):


        self.logger.info(
            f"Main request: {message}"
        )



        decision = self.decision_agent.process(
            message
        )


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



        return orchestrator.run(
            message,
            decision,
            conversation
        )