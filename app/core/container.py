from tools.tool_registry import ToolRegistry

from tools.calculator import Calculator
from tools.file_tool import FileTool
from tools.memory_tool import MemoryTool
from tools.formatter_tool import FormatterTool
from tools.code_repair_tool import CodeRepairTool
from tools.code_analyzer_tool import CodeAnalyzerTool


from agents.planner_agent import PlannerAgent
from agents.tool_agent import ToolAgent
from agents.chat_agent import ChatAgent


from memory.memory import Memory
from memory.chat_manager import ChatManager


from models.llm_provider import LLMProvider
from config.config_manager import ConfigManager


from app.core.orchestrator.orchestrator import Orchestrator





class AIContainer:


    def __init__(self):


        #
        # Config
        #

        self.config = ConfigManager()



        #
        # Core
        #

        self.memory = Memory()


        self.chat_manager = ChatManager()



        #
        # LLM
        #

        self.llm = LLMProvider(

            self.config

        )




        #
        # Tools
        #

        self.registry = ToolRegistry()


        self._register_tools()




        #
        # Agents
        #

        self.planner = PlannerAgent(

            self.memory,

            self.llm

        )



        self.chat_agent = ChatAgent(

            self.memory,

            self.llm

        )



        self.tool_agent = ToolAgent(

            self.registry,

            self.memory

        )





        #
        # Orchestrator
        #

        self.orchestrator = Orchestrator(

            self.planner,

            {
                "chat": self.chat_agent,

                "tool": self.tool_agent
            }

        )






    def _register_tools(self):


        self.registry.register(

            "calculator",

            Calculator()

        )



        self.registry.register(

            "file",

            FileTool()

        )




        memory_tool = MemoryTool(

            self.memory

        )



        self.registry.register(

            "memory",

            memory_tool

        )


        self.registry.register(

            "memory_save",

            memory_tool

        )


        self.registry.register(

            "memory_get",

            memory_tool

        )





        self.registry.register(

            "formatter",

            FormatterTool()

        )




        self.registry.register(

            "code_repair",

            CodeRepairTool(

                self.llm

            )

        )



        self.registry.register(

            "code_analyzer",

            CodeAnalyzerTool(

                self.llm

            )

        )