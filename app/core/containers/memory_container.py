from memory.memory import Memory
from memory.chat_manager import ChatManager
from memory.project_memory.project_memory import ProjectMemory

from app.core.orchestrators.memory_orchestrator import MemoryOrchestrator


class MemoryContainer:


    def __init__(
        self,
        core
    ):

        self.memory = Memory()


        self.chat_manager = ChatManager()


        self.project_memory = ProjectMemory(
            core.workspace_path
        )


        self.orchestrator = None



    def attach_agents(
        self,
        agents
    ):

        self.orchestrator = MemoryOrchestrator(
            agents
        )