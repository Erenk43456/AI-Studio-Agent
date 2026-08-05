from app.core.containers.core_container import CoreContainer
from app.core.containers.model_container import ModelContainer
from app.core.containers.memory_container import MemoryContainer
from app.core.containers.tool_container import ToolContainer
from app.core.containers.agent_container import AgentContainer
from app.core.containers.chat_container import ChatContainer
from app.core.containers.development_container import DevelopmentContainer



class MainContainer:


    def __init__(self):


        self.core = CoreContainer()


        #
        # Models
        #

        self.models = ModelContainer(
            self.core
        )


        #
        # Memory
        #

        self.memory = MemoryContainer(
            self.core
        )


        #
        # Tools
        #

        self.tools = ToolContainer(
            self.core,
            self.models
        )


        #
        # Agents
        #

        self.agents = AgentContainer(
            self
        )


        #
        # Systems
        #

        self.chat = ChatContainer(
            self
        )


        self.development = DevelopmentContainer(
            self
        )