import pytest

from agents.base_agent import BaseAgent


class AgentDouble(BaseAgent):

    def run(self, task):

        return f"completed: {task}"


class MemoryDouble:

    def __init__(self):

        self.data = {}

    def save(self, key, value):

        self.data[key] = value

    def recall(self):

        return dict(self.data)


@pytest.mark.contract
def test_agent_has_name():

    agent = AgentDouble(
        "contract-agent"
    )

    assert agent.name == "contract-agent"


@pytest.mark.contract
def test_agent_has_run_method():

    agent = AgentDouble(
        "contract-agent"
    )

    assert callable(
        agent.run
    )


@pytest.mark.contract
def test_agent_run_returns_result():

    agent = AgentDouble(
        "contract-agent"
    )

    result = agent.run(
        "hello"
    )

    assert result == (
        "completed: hello"
    )


@pytest.mark.contract
def test_agent_can_use_memory():

    memory = MemoryDouble()

    agent = AgentDouble(
        "contract-agent",
        memory=memory,
    )

    agent.remember(
        "language",
        "Python",
    )

    assert memory.data == {
        "contract-agent:language": "Python"
    }


@pytest.mark.contract
def test_agent_can_recall_memory():

    memory = MemoryDouble()

    memory.save(
        "contract-agent:language",
        "Python",
    )

    agent = AgentDouble(
        "contract-agent",
        memory=memory,
    )

    result = agent.recall()

    assert result[
        "contract-agent:language"
    ] == "Python"


@pytest.mark.contract
def test_agent_without_memory_is_valid():

    agent = AgentDouble(
        "contract-agent"
    )

    assert agent.memory is None

    assert agent.recall() is None