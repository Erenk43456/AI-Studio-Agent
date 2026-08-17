import pytest

from agents.planner.llm_planner import create_llm_plan
from agents.tool_agent import ToolAgent

from tests.fakes.fake_llm import FakeLLM
from tests.fakes.fake_tool import FakeTool


class FakeToolRegistry:

    def __init__(self, tools):
        self.tools = tools

    def get(self, name):
        return self.tools.get(name)


@pytest.mark.integration
def test_planner_creates_valid_tool_plan():

    llm = FakeLLM(
        response="""
        {
            "steps": [
                {
                    "tool": "fake_tool",
                    "action": "execute",
                    "input": "hello"
                }
            ]
        }
        """
    )

    plan = create_llm_plan(
        llm,
        "run the fake tool",
        [
            {
                "name": "fake_tool",
                "description": "A deterministic test tool.",
                "purpose": "Testing tool execution.",
            }
        ],
    )

    assert plan is not None
    assert "steps" in plan
    assert len(plan["steps"]) == 1

    step = plan["steps"][0]

    assert step["tool"] == "fake_tool"
    assert step["action"] == "execute"


@pytest.mark.integration
def test_planner_plan_executes_through_tool_agent():

    llm = FakeLLM(
        response="""
        {
            "steps": [
                {
                    "tool": "fake_tool",
                    "action": "execute",
                    "input": "hello"
                }
            ]
        }
        """
    )

    fake_tool = FakeTool(
        result="tool result"
    )

    registry = FakeToolRegistry(
        {
            "fake_tool": fake_tool
        }
    )

    plan = create_llm_plan(
        llm,
        "run the fake tool",
        [
            {
                "name": "fake_tool",
                "description": "A deterministic test tool.",
                "purpose": "Testing tool execution.",
            }
        ],
    )

    agent = ToolAgent(
        registry=registry,
        llm=llm,
    )

    result = agent.execute_steps(
        plan
    )

    assert fake_tool.call_count == 1
    assert result[0]["tool"] == "fake_tool"
    assert result[0]["result"] == "tool result"


@pytest.mark.integration
def test_planner_to_tool_pipeline_preserves_input():

    llm = FakeLLM(
        response="""
        {
            "steps": [
                {
                    "tool": "fake_tool",
                    "action": "execute",
                    "input": "important test input"
                }
            ]
        }
        """
    )

    fake_tool = FakeTool(
        result="success"
    )

    registry = FakeToolRegistry(
        {
            "fake_tool": fake_tool
        }
    )

    plan = create_llm_plan(
        llm,
        "execute the test",
        [
            {
                "name": "fake_tool",
                "description": "A deterministic test tool.",
                "purpose": "Testing tool execution.",
            }
        ],
    )

    agent = ToolAgent(
        registry=registry,
        llm=llm,
    )

    agent.execute_steps(
        plan
    )

    assert fake_tool.call_count == 1

    call = fake_tool.calls[0]

    assert call["args"][0]["input"] == "important test input"