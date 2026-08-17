from app.core.orchestrators.chat_orchestrator import ChatOrchestrator


class ChatContainer:

    def __init__(
        self,
        main
    ):

        self.llm = main.models.chat_llm


        self.memory = main.memory.memory


        self.chat_manager = main.memory.chat_manager


        self.project_memory = (
            main.memory.project_memory
        )


        self.chat_agent = main.agents.chat


        self.orchestrator = ChatOrchestrator(

            self

        )