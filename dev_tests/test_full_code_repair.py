from tools.tool_registry import ToolRegistry

from tools.code_repair_tool import CodeRepairTool

from agents.tool_agent import ToolAgent


registry = ToolRegistry()


registry.register(
    "code_repair",
    CodeRepairTool()
)


agent = ToolAgent(
    registry
)


plan = {

    "tool": "code_repair",

    "code": """
def test(
    print("hello")
"""
}


result = agent.execute(
    plan
)


print(result)