import pytest

from agents.base_agent import BaseAgent
from tests.fakes.fake_memory import FakeMemory


class IntegrationAgent(BaseAgent):

    def run(self, task):

        self.remember(
            "last_task",
            task,
        )

        return task


@pytest.mark.integration
def test_agent_persists_memory():

    memory = FakeMemory()

    agent = IntegrationAgent(
        "integration-agent",
        memory=memory,
    )

    agent.run(
        "build project"
    )

    assert memory.get(
        "integration-agent:last_task"
    ) == "build project"


@pytest.mark.integration
def test_agent_recall_returns_memory():

    memory = FakeMemory()

    agent = IntegrationAgent(
        "integration-agent",
        memory=memory,
    )

    agent.remember(
        "language",
        "Python",
    )

    result = agent.recall()

    assert result[
        "integration-agent:language"
    ]["value"] == "Python"


@pytest.mark.integration
def test_multiple_memory_entries_survive():

    memory = FakeMemory()

    agent = IntegrationAgent(
        "integration-agent",
        memory=memory,
    )

    agent.remember(
        "language",
        "Python",
    )

    agent.remember(
        "framework",
        "PySide6",
    )

    result = agent.recall()

    assert result[
        "integration-agent:language"
    ]["value"] == "Python"

    assert result[
        "integration-agent:framework"
    ]["value"] == "PySide6"