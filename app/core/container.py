from tools.tool_registry import ToolRegistry

from tools.calculator import Calculator
from tools.file_tool import FileTool
from tools.memory_tool import MemoryTool
from tools.formatter_tool import FormatterTool
from tools.code_repair_tool import CodeRepairTool
from tools.code_analyzer_tool import CodeAnalyzerTool
from tools.repository_analyzer import RepositoryAnalyzerTool
from tools.code_writer_tool import CodeWriterTool
from tools.project_memory_tool import ProjectMemoryTool


from agents.planner_agent import PlannerAgent
from agents.tool_agent import ToolAgent
from agents.chat_agent import ChatAgent
from agents.code_agent import CodeAgent


from memory.memory import Memory
from memory.chat_manager import ChatManager
from memory.project_memory.project_memory import ProjectMemory


from models.llm_provider import LLMProvider
from config.config_manager import ConfigManager


from app.core.orchestrator.orchestrator import Orchestrator
from app.core.workspace.workspace_manager import WorkspaceManager
from app.core.workspace.watcher import WorkspaceWatcher





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
        # Workspace
        #

        self.workspace = WorkspaceManager(
            r"C:\AI-Studio"
        )


        self.workspace_path = (
            self.workspace.create_workspace()
        )


        print(
            "WORKSPACE:",
            self.workspace_path
        )

        self.project_memory = ProjectMemory(
            self.workspace_path
        )


        #
        # LLM
        #

        self.llm = LLMProvider(
            self.config
        )





        #
        # Registry
        #

        self.registry = ToolRegistry()


        #
        # Agents
        #

        self.planner = PlannerAgent(
            self.llm,
            self.memory,
            self.registry
        )



        self.chat_agent = ChatAgent(
            llm=self.llm,
            memory=self.memory,
            conversation=None,
            project_memory=self.project_memory
        )



        self.tool_agent = ToolAgent(
            self.registry,
            self.memory
        )



        self.code_agent = CodeAgent(
            self.llm,
            self.registry,
            self.memory,
            self.workspace_path
        )





        #
        # Tools
        #

        self._register_tools()





        #
        # Watcher
        #

        self.watcher = WorkspaceWatcher(
            self.workspace_path,
            self.refresh_project_memory
        )





        #
        # Orchestrator
        #

        self.orchestrator = Orchestrator(

            self.planner,

            {

                "chat": self.chat_agent,

                "tool": self.tool_agent,

                "code": self.code_agent

            }

        )


    def refresh_project_memory(
        self,
        changed_files=None
    ):

        analyzer = self.registry.get(
            "repository_analyzer"
        )

        if analyzer:
            analyzer.execute(
                {
                    "action":"analyze",
                    "changed_files": changed_files
                }
            )


    def _register_tools(self):



        self.registry.register(

            "code",

            self.code_agent,

            {

                "description":
                "Autonomous software engineering agent.",

                "purpose":
                "Analyze architecture and create implementation plans.",

                "safe": False,

                "modifies_files": True

            }

        )





        self.registry.register(

            "calculator",

            Calculator(),

            {

                "description":
                "Perform calculations.",

                "purpose":
                "Math operations.",

                "safe": True,

                "modifies_files": False

            }

        )





        self.registry.register(

            "file",

            FileTool(

                self.workspace_path

            ),

            {

                "description":
                "Workspace file operations.",

                "purpose":
                "Read and modify workspace files.",

                "safe": False,

                "modifies_files": True

            }

        )





        memory_tool = MemoryTool(

            self.memory

        )


        memory_metadata = {


            "description":
            "Memory management.",


            "purpose":
            "Store and retrieve information.",


            "safe": True,


            "modifies_files": False

        }




        self.registry.register(

            "memory",

            memory_tool,

            memory_metadata

        )


        self.registry.register(

            "memory_save",

            memory_tool,

            memory_metadata

        )


        self.registry.register(

            "memory_get",

            memory_tool,

            memory_metadata

        )







        self.registry.register(

            "formatter",

            FormatterTool(

                self.workspace_path

            ),

            {

                "description":
                "Format workspace code.",


                "purpose":
                "Code formatting.",


                "safe": True,


                "modifies_files": True

            }

        )








        self.registry.register(

            "code_repair",

            CodeRepairTool(

                self.llm,

                self.workspace_path

            ),

            {

                "description":
                "Repair workspace code.",


                "purpose":
                "Fix programming errors.",


                "safe": False,


                "modifies_files": True

            }

        )







        self.registry.register(

            "code_analyzer",

            CodeAnalyzerTool(

                self.llm,

                self.workspace_path

            ),

            {

                "description":
                "Analyze workspace source code.",


                "purpose":
                "Review code.",


                "safe": True,


                "modifies_files": False

            }

        )







        self.registry.register(

            "code_writer",

            CodeWriterTool(

                self.llm,

                self.workspace_path

            ),

            {

                "description":
                "Apply CodeAgent implementation changes.",


                "purpose":
                "Generate and write code modifications.",


                "safe": False,


                "modifies_files": True

            }

        )



        self.registry.register(

            "project_memory",

            ProjectMemoryTool(
                self.project_memory
            ),

            {

                "description":
                "Persistent project knowledge memory.",


                "purpose":
                "Provides architecture and codebase context.",


                "safe":
                True,


                "modifies_files":
                False

            }

        )




        self.registry.register(

            "repository_analyzer",

            RepositoryAnalyzerTool(

                self.workspace_path,
                self.memory,
                self.project_memory

            ),

            {

                "description":
                "Analyze workspace repository.",


                "purpose":
                "Understand project structure.",


                "safe": True,


                "modifies_files": False

            }

        )