import pytest

import agents.planner_agent as module

from agents.planner_agent import PlannerAgent
from tests.fakes.fake_llm import FakeLLM
from tests.fakes.fake_memory import FakeMemory
from tests.fakes.fake_registry import FakeRegistry


@pytest.mark.unit
def test_planner_empty_task_returns_empty_plan():

    agent = PlannerAgent(
        FakeLLM()
    )

    result = agent.create_plan("")

    assert result == {
        "steps": []
    }


@pytest.mark.unit
def test_planner_none_task_returns_empty_plan():

    agent = PlannerAgent(
        FakeLLM()
    )

    result = agent.create_plan(None)

    assert result == {
        "steps": []
    }


@pytest.mark.unit
def test_planner_saves_last_task():

    memory = FakeMemory()

    agent = PlannerAgent(
        FakeLLM(),
        memory=memory
    )

    agent.create_plan("Fix the bug")

    assert memory.calls == [
        (
            "last_task",
            "Fix the bug",
            "system"
        )
    ]


@pytest.mark.unit
def test_planner_accepts_valid_llm_plan(monkeypatch):

    monkeypatch.setattr(
        module,
        "create_llm_plan",
        lambda *args: {
            "steps": [
                {
                    "tool": "calculator",
                    "action": "calculate",
                    "input": "2 + 2"
                }
            ]
        }
    )

    registry = FakeRegistry(
        {
            "calculator": object()
        }
    )

    agent = PlannerAgent(
        FakeLLM(),
        registry=registry
    )

    result = agent.create_plan(
        "Calculate 2 + 2"
    )

    assert result == {
        "steps": [
            {
                "tool": "calculator",
                "action": "calculate",
                "input": "2 + 2"
            }
        ],
        "user_message": "Calculate 2 + 2"
    }


@pytest.mark.unit
def test_planner_rejects_unknown_tool(monkeypatch):

    monkeypatch.setattr(
        module,
        "create_llm_plan",
        lambda *args: {
            "steps": [
                {
                    "tool": "unknown_tool",
                    "action": "execute",
                    "input": "test"
                }
            ]
        }
    )

    registry = FakeRegistry()

    agent = PlannerAgent(
        FakeLLM(),
        registry=registry
    )

    result = agent.create_plan(
        "Do something"
    )

    assert result["steps"][0]["tool"] == "code"
    assert result["steps"][0]["action"] == "implement"


@pytest.mark.unit
def test_planner_invalid_steps_use_fallback(monkeypatch):

    monkeypatch.setattr(
        module,
        "create_llm_plan",
        lambda *args: {
            "steps": []
        }
    )

    agent = PlannerAgent(
        FakeLLM()
    )

    result = agent.create_plan(
        "Fix the Python bug"
    )

    assert result["steps"] == [
        {
            "tool": "code",
            "action": "implement",
            "input": "Fix the Python bug"
        }
    ]


@pytest.mark.unit
def test_planner_invalid_plan_uses_fallback(monkeypatch):

    monkeypatch.setattr(
        module,
        "create_llm_plan",
        lambda *args: None
    )

    agent = PlannerAgent(
        FakeLLM()
    )

    result = agent.create_plan(
        "Fix the bug"
    )

    assert result["steps"] == [
        {
            "tool": "code",
            "action": "implement",
            "input": "Fix the bug"
        }
    ]


@pytest.mark.unit
def test_planner_exception_uses_fallback(monkeypatch):

    def fail(*args):
        raise RuntimeError("planner failed")

    monkeypatch.setattr(
        module,
        "create_llm_plan",
        fail
    )

    agent = PlannerAgent(
        FakeLLM()
    )

    result = agent.create_plan(
        "Fix the bug"
    )

    assert result["steps"] == [
        {
            "tool": "code",
            "action": "implement",
            "input": "Fix the bug"
        }
    ]


@pytest.mark.unit
def test_planner_analysis_fallback_uses_repository_analyzer(
    monkeypatch
):

    monkeypatch.setattr(
        module,
        "create_llm_plan",
        lambda *args: None
    )

    registry = FakeRegistry(
        {
            "repository_analyzer": object()
        }
    )

    agent = PlannerAgent(
        FakeLLM(),
        registry=registry
    )

    result = agent.create_plan(
        "Analyze the repository architecture"
    )

    assert result["steps"] == [
        {
            "tool": "repository_analyzer",
            "action": "analyze",
            "input": "Analyze the repository architecture"
        }
    ]


@pytest.mark.unit
def test_planner_preserves_user_message(monkeypatch):

    monkeypatch.setattr(
        module,
        "create_llm_plan",
        lambda *args: {
            "steps": [
                {
                    "tool": "calculator",
                    "action": "calculate",
                    "input": "10 + 5"
                }
            ]
        }
    )

    registry = FakeRegistry(
        {
            "calculator": object()
        }
    )

    agent = PlannerAgent(
        FakeLLM(),
        registry=registry
    )

    task = "Calculate 10 + 5"

    result = agent.create_plan(task)

    assert result["user_message"] == task

@pytest.mark.unit
def test_planner_calculation_fallback_uses_calculator():
    agent = PlannerAgent(
        FakeLLM(),
        FakeMemory(),
        FakeRegistry(
            {
                "calculator": object(),
            }
        ),
    )

    result = agent._fallback_plan("15 + 20 kaç eder?")

    assert result["steps"] == [
        {
            "tool": "calculator",
            "action": "calculate",
            "input": "15 + 20 kaç eder?",
        }
    ]