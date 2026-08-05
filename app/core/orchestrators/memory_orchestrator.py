from app.core.logger import AppLogger



class MemoryOrchestrator:


    def __init__(
        self,
        agents
    ):


        self.memory_agent = (
            agents.memory
        )


        self.logger = AppLogger()



    def run(
        self,
        message,
        decision=None,
        conversation=None
    ):


        self.logger.info(
            f"Memory request: {message}"
        )



        if not decision:

            return (
                "Memory decision missing."
            )



        action = decision.get(
            "action"
        )



        if action == "save":


            return self.memory_agent.save(
                message
            )



        if action == "get":


            return self.memory_agent.get(
                message
            )



        return (
            "Unknown memory action."
        )