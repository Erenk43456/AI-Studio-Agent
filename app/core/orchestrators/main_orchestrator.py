class MainOrchestrator:


    def __init__(self, container):


        self.container = container


        self.decision_agent = (
            container.agents.decision_agent
        )


        self.systems = {

            "memory":
            container.memory.orchestrator,


            "chat":
            container.chat.orchestrator,


            "development":
            container.development.orchestrator

        }



    def run(self,message):


        decision = self.decision_agent.process(
            message
        )


        system = decision.get(
            "system",
            "chat"
        )


        orchestrator = self.systems.get(
            system
        )


        if not orchestrator:

            return "Unknown system"


        return orchestrator.run(
            message,
            decision
        )