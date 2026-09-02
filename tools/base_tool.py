from contracts.tool_contract import ToolContract


class BaseTool(ToolContract):

    name = None
    description = None

    def execute(
        self,
        data
    ):
        raise NotImplementedError(
            "Tool must implement execute()"
        )