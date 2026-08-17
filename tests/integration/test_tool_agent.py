import pytest

from agents.tool_agent import ToolAgent
from tests.fakes.fake_tool import FakeTool
from tests.fakes.fake_memory import FakeMemory


class FakeToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, name, tool):
        self.tools[name] = tool

    def get(self, name):
        return self.tools.get(name)


@pytest.mark.integration
def test_tool_agent_executes_registered_tool():

    registry = FakeToolRegistry()

    tool = FakeTool(
        name="fake_tool",
        result="tool-result",
    )

    registry.register(
        "fake_tool",
        tool,
    )

    agent = ToolAgent(
        registry=registry,
        memory=FakeMemory(),
    )

    result = agent.execute(
        {
            "tool": "fake_tool",
            "action": "run",
            "input": "hello",
        }
    )

    assert result == "tool-result"

    assert tool.call_count == 1

    assert tool.calls[0]["args"][0]["tool"] == "fake_tool"


@pytest.mark.integration
def test_tool_agent_returns_error_for_unknown_tool():

    registry = FakeToolRegistry()

    agent = ToolAgent(
        registry=registry,
        memory=FakeMemory(),
    )

    result = agent.execute(
        {
            "tool": "missing_tool",
            "action": "run",
        }
    )

    assert result == "Tool not found: missing_tool"


@pytest.mark.integration
def test_tool_agent_executes_multiple_steps():

    registry = FakeToolRegistry()

    tool = FakeTool(
        name="fake_tool",
        result="step-result",
    )

    registry.register(
        "fake_tool",
        tool,
    )

    agent = ToolAgent(
        registry=registry,
        memory=FakeMemory(),
    )

    plan = {
        "steps": [
            {
                "tool": "fake_tool",
                "action": "run",
                "input": "first",
            },
            {
                "tool": "fake_tool",
                "action": "run",
                "input": "second",
            },
        ]
    }

    result = agent.execute_steps(
        plan
    )

    assert len(result) == 2

    assert result[0]["step"] == 1
    assert result[1]["step"] == 2

    assert result[0]["tool"] == "fake_tool"
    assert result[1]["tool"] == "fake_tool"

    assert result[0]["result"] == "step-result"
    assert result[1]["result"] == "step-result"

    assert tool.call_count == 2


@pytest.mark.integration
def test_tool_agent_normalizes_file_write_input():

    registry = FakeToolRegistry()

    agent = ToolAgent(
        registry=registry,
        memory=FakeMemory(),
    )

    plan = {
        "tool": "file",
        "action": "write",
        "filename": "test.py",
        "input": "print('hello')",
    }

    result = agent.normalize_tool_input(
        plan
    )

    assert result["content"] == "print('hello')"


@pytest.mark.integration
def test_tool_agent_normalizes_calculator_input():

    registry = FakeToolRegistry()

    agent = ToolAgent(
        registry=registry,
        memory=FakeMemory(),
    )

    plan = {
        "tool": "calculator",
        "input": "10 + 5",
    }

    result = agent.normalize_tool_input(
        plan
    )

    assert result["operation"] == "add"
    assert result["numbers"] == ["10", "5"]