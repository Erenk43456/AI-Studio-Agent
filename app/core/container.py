from tools.tool_registry import ToolRegistry
from tools.calculator import Calculator
from tools.file_tool import FileTool
from tools.memory_tool import MemoryTool

from agents.planner_agent import PlannerAgent
from agents.tool_agent import ToolAgent
from agents.chat_agent import ChatAgent

from memory.memory import Memory
from memory.conversation import ConversationMemory



class AIContainer:


    def __init__(self):

        self.memory = Memory()

        self.conversation = ConversationMemory()


        self.registry = ToolRegistry()


        self.registry.register(
            "calculator",
            Calculator()
        )


        self.registry.register(
            "file",
            FileTool()
        )


        self.registry.register(
            "memory",
            MemoryTool(
                self.memory
            )
        )


        self.planner = PlannerAgent(
            self.memory
        )


        self.tool_agent = ToolAgent(
            self.registry,
            self.memory
        )


        self.chat_agent = ChatAgent(
            self.memory
        )