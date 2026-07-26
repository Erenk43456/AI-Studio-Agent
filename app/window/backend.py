from tools.tool_registry import ToolRegistry

from tools.calculator import Calculator
from tools.file_tool import FileTool
from tools.memory_tool import MemoryTool


from agents.planner_agent import PlannerAgent
from agents.tool_agent import ToolAgent
from agents.chat_agent import ChatAgent


from memory.memory import Memory
from memory.conversation import ConversationMemory
from memory.chat_manager import ChatManager


class Backend:


    @staticmethod
    def setup(window):


        window.memory = Memory()


        window.chat_manager = ChatManager()


        chats = window.chat_manager.list_chats()


        if chats:

            chat = chats[0]

        else:

            chat = window.chat_manager.create_chat()



        window.current_chat = chat.id


        window.conversation = chat.conversation


        window.planner = PlannerAgent(
            window.memory
        )


        registry = ToolRegistry()


        registry.register(
            "calculator",
            Calculator()
        )


        registry.register(
            "file",
            FileTool()
        )


        registry.register(
            "memory",
            MemoryTool(
                window.memory
            )
        )



        window.registry = registry



        window.tool_agent = ToolAgent(
            registry,
            window.memory
        )



        window.chat_agent = ChatAgent(
            window.memory
        )