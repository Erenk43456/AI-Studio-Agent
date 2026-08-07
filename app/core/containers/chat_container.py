from agents.chat_agent import ChatAgent
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


        self.chat_agent = ChatAgent(

            llm=self.llm,

            memory=self.memory,

            conversation=None,

            project_memory=self.project_memory

        )


        self.orchestrator = ChatOrchestrator(

            self

        )