import pytest

from app.core.containers.agent_container import AgentContainer
from agents.decision_agent import DecisionAgent
from agents.chat_agent import ChatAgent
from agents.code_agent import CodeAgent
from agents.memory_agent import MemoryAgent


class FakeLLM:
    pass


class FakeMemory:
    pass


class FakeRegistry:
    pass


class FakeCore:
    workspace_path = "C:/AI-Studio"


class FakeModels:
    decision_llm = FakeLLM()
    chat_llm = FakeLLM()
    code_llm = FakeLLM()


class FakeMemoryContainer:
    memory = FakeMemory()


class FakeTools:
    registry = FakeRegistry()


class FakeMain:
    models = FakeModels()
    memory = FakeMemoryContainer()
    tools = FakeTools()
    core = FakeCore()


@pytest.mark.unit
def test_agent_container_creates_agents():

    container = AgentContainer(
        FakeMain()
    )

    assert isinstance(
        container.decision,
        DecisionAgent,
    )

    assert isinstance(
        container.chat,
        ChatAgent,
    )

    assert isinstance(
        container.code,
        CodeAgent,
    )

    assert isinstance(
        container.memory,
        MemoryAgent,
    )


@pytest.mark.unit
def test_agent_container_creates_all_agents():

    container = AgentContainer(
        FakeMain()
    )

    assert container.decision is not None
    assert container.chat is not None
    assert container.code is not None
    assert container.memory is not None