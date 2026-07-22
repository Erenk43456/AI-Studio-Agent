from tools.tool_registry import ToolRegistry
from tools.calculator import Calculator



def test_register_tool():


    registry = ToolRegistry()


    calculator = Calculator()


    registry.register(
        "calculator",
        calculator
    )


    tools = registry.list_tools()


    assert "calculator" in tools





def test_get_tool():


    registry = ToolRegistry()


    calculator = Calculator()


    registry.register(
        "calculator",
        calculator
    )


    tool = registry.get(
        "calculator"
    )


    assert tool is not None


    assert isinstance(
        tool,
        Calculator
    )