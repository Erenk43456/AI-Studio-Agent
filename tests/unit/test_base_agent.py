import pytest

from agents.base_agent import BaseAgent


class AgentUnderTest(BaseAgent):

    def run(self, task):

        return f"ran: {task}"


class MemoryDouble:

    def __init__(self):

        self.data = {}

    def save(self, key, value):

        self.data[key] = value

    def recall(self):

        return dict(self.data)


@pytest.mark.unit
def test_agent_initializes():

    memory = MemoryDouble()

    agent = AgentUnderTest(
        "test-agent",
        memory=memory,
    )

    assert agent.name == "test-agent"
    assert agent.memory is memory


@pytest.mark.unit
def test_agent_remember():

    memory = MemoryDouble()

    agent = AgentUnderTest(
        "test-agent",
        memory=memory,
    )

    agent.remember(
        "key",
        "value",
    )

    assert memory.data[
        "test-agent:key"
    ] == "value"


@pytest.mark.unit
def test_agent_recall():

    memory = MemoryDouble()

    agent = AgentUnderTest(
        "test-agent",
        memory=memory,
    )

    memory.save(
        "test-agent:key",
        "value",
    )

    result = agent.recall()

    assert result[
        "test-agent:key"
    ] == "value"


@pytest.mark.unit
def test_agent_without_memory():

    agent = AgentUnderTest(
        "test-agent"
    )

    agent.remember(
        "key",
        "value",
    )

    assert agent.recall() is None


@pytest.mark.unit
def test_agent_run():

    agent = AgentUnderTest(
        "test-agent"
    )

    result = agent.run(
        "hello"
    )

    assert result == "ran: hello"