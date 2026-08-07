from agents.decision_agent import DecisionAgent
from agents.chat_agent import ChatAgent
from agents.code_agent import CodeAgent
from agents.memory_agent import MemoryAgent


class AgentContainer:


    def __init__(
        self,
        main
    ):


        #
        # Decision Agent
        #

        self.decision = DecisionAgent(

            main.models.decision_llm,

            main.memory.memory,

            main.tools.registry

        )



        #
        # Chat Agent
        #

        self.chat = ChatAgent(

            main.models.chat_llm,

            main.memory.memory

        )



        #
        # Code Agent
        #

        self.code = CodeAgent(

            main.models.code_llm,

            main.tools.registry,

            main.memory.memory,

            main.core.workspace_path

        )

        #
        # Memory Agent
        #

        self.memory = MemoryAgent(

            main.memory.memory

        )