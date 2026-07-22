from tools.tool_registry import ToolRegistry

from tools.calculator import Calculator
from tools.file_tool import FileTool
from tools.memory_tool import MemoryTool


from agents.planner_agent import PlannerAgent
from agents.tool_agent import ToolAgent
from agents.chat_agent import ChatAgent


from memory.memory import Memory
from memory.conversation import ConversationMemory



class Backend:


    @staticmethod
    def setup(window):


        window.memory = Memory()


        window.conversation = ConversationMemory()



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