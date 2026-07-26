from tools.tool_registry import ToolRegistry
from tools.formatter_tool import FormatterTool
from agents.tool_agent import ToolAgent


registry = ToolRegistry()


registry.register(
    "formatter",
    FormatterTool()
)


agent = ToolAgent(
    registry
)


plan = {
    "tool": "formatter",
    "action": "code",
    "code": """
def test():
        print("Merhaba")
        if True:
                print("Bozuk")
"""
}


result = agent.execute(
    plan
)


print(result)