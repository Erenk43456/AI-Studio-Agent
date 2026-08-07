from tools.tool_registry import ToolRegistry

from tools.calculator import Calculator
from tools.file_tool import FileTool
from tools.code_writer_tool import CodeWriterTool
from tools.code_analyzer_tool import CodeAnalyzerTool
from tools.code_repair_tool import CodeRepairTool


class ToolContainer:


    def __init__(
        self,
        core,
        models
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

            core.workspace_path

        )


        self.code_analyzer = CodeAnalyzerTool(

            models.code_llm,

            core.workspace_path

        )


        self.code_repair = CodeRepairTool(

            models.code_llm,

            core.workspace_path

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