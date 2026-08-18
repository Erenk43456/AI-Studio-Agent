from tools.tool_registry import ToolRegistry

from tools.calculator import Calculator
from tools.file_tool import FileTool
from tools.code_writer_tool import CodeWriterTool
from tools.code_analyzer_tool import CodeAnalyzerTool
from tools.code_repair_tool import CodeRepairTool
from tools.repository_analyzer import RepositoryAnalyzerTool
from tools.project_memory_tool import ProjectMemoryTool
from tools.memory_tool import MemoryTool
from tools.formatter_tool import FormatterTool


class ToolContainer:

    def __init__(
        self,
        core,
        models,
        memory
    ):

        #
        # Registry
        #

        self.registry = ToolRegistry()


        #
        # Basic tools
        #

        self.calculator = Calculator()

        self.file_tool = FileTool(
            core.workspace_path
        )


        #
        # Code tools
        #

        self.code_writer = CodeWriterTool(
            models.code_llm,
            core.workspace_path,
            self.registry
        )

        self.code_analyzer = CodeAnalyzerTool(
            models.code_llm,
            core.workspace_path
        )

        self.code_repair = CodeRepairTool(
            models.code_llm,
            core.workspace_path
        )

        self.formatter = FormatterTool(
            core.workspace_path
        )


        #
        # Repository Analyzer
        #

        self.repository_analyzer = RepositoryAnalyzerTool(
            root=core.workspace_path,
            memory=memory,
        )

        #
        # Project Memory
        #

        self.project_memory = ProjectMemoryTool(
            memory.project_memory
        )

        #
        # User Memory
        #

        self.memory_tool = MemoryTool(
            memory.memory
        )


        #
        # Register
        #

        self.registry.register(
            "calculator",
            self.calculator
        )

        self.registry.register(
            "file",
            self.file_tool
        )

        self.registry.register(
            "code_writer",
            self.code_writer
        )

        self.registry.register(
            "code_analyzer",
            self.code_analyzer
        )

        self.registry.register(
            "code_repair",
            self.code_repair
        )

        self.registry.register(
            "repository_analyzer",
            self.repository_analyzer
        )

        self.registry.register(
            "project_memory",
            self.project_memory
        )

        self.registry.register(
            "memory",
            self.memory_tool
        )

        self.registry.register(
            "formatter",
            self.formatter
        )