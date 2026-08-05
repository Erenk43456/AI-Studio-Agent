from config.config_manager import ConfigManager

from memory.memory import Memory
from memory.chat_manager import ChatManager
from memory.project_memory.project_memory import ProjectMemory

from tools.tool_registry import ToolRegistry

from app.core.workspace.workspace_manager import WorkspaceManager



class CoreContainer:


    def __init__(self):


        #
        # CONFIG
        #

        self.config = ConfigManager()



        #
        # GLOBAL MEMORY
        #

        self.memory = Memory()


        self.chat_manager = ChatManager()



        #
        # WORKSPACE
        #

        self.workspace = WorkspaceManager(
            r"C:\AI-Studio"
        )


        self.workspace_path = (
            self.workspace.create_workspace()
        )



        #
        # PROJECT MEMORY
        #

        self.project_memory = ProjectMemory(
            self.workspace_path
        )