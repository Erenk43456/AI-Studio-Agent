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




class Backend:


    @staticmethod
    def setup(window):


        # -------------------------
        # Memory
        # -------------------------

        window.memory = Memory()





        # -------------------------
        # Chat Manager
        # -------------------------

        window.chat_manager = ChatManager()



        chats = window.chat_manager.list_chats()



        if chats:

            chat = chats[0]


        else:

            chat = window.chat_manager.create_chat()





        window.current_chat = chat.id

        window.conversation = chat.conversation







        # -------------------------
        # Planner Agent
        # -------------------------

        window.planner = PlannerAgent(

            window.memory

        )









        # -------------------------
        # Tool Registry
        # -------------------------

        registry = ToolRegistry()



        calculator = Calculator()

        file_tool = FileTool()

        memory_tool = MemoryTool(

            window.memory

        )

        formatter = FormatterTool()

        code_repair = CodeRepairTool()

        code_analyzer = CodeAnalyzerTool()







        registry.register(

            "calculator",

            calculator

        )



        registry.register(

            "file",

            file_tool

        )



        registry.register(

            "memory",

            memory_tool

        )



        registry.register(

            "memory_save",

            memory_tool

        )



        registry.register(

            "memory_get",

            memory_tool

        )



        registry.register(

            "formatter",

            formatter

        )



        registry.register(

            "code_repair",

            code_repair

        )



        registry.register(

            "code_analyzer",

            code_analyzer

        )







        window.registry = registry







        # -------------------------
        # Chat Agent
        # -------------------------

        window.chat_agent = ChatAgent(

            window.memory

        )







        # -------------------------
        # Tool Agent
        # -------------------------

        window.tool_agent = ToolAgent(

            registry,

            window.memory,

            window.chat_agent

        )