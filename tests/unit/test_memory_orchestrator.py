import pytest

from app.core.orchestrators.memory_orchestrator import (
    MemoryOrchestrator,
)


class FakeMemoryAgent:

    def __init__(self):
        self.save_calls = []
        self.get_calls = []

    def save(self, message):
        self.save_calls.append(message)
        return "save result"

    def get(self, message):
        self.get_calls.append(message)
        return "get result"


class FakeAgents:

    def __init__(self):
        self.memory = FakeMemoryAgent()


@pytest.mark.unit
def test_memory_orchestrator_save():

    agents = FakeAgents()
    orchestrator = MemoryOrchestrator(agents)

    result = orchestrator.run(
        "benim adım Eren",
        {"action": "save"},
    )

    assert result == "save result"
    assert agents.memory.save_calls == [
        "benim adım Eren"
    ]


@pytest.mark.unit
def test_memory_orchestrator_get():

    agents = FakeAgents()
    orchestrator = MemoryOrchestrator(agents)

    result = orchestrator.run(
        "ismim ne",
        {"action": "get"},
    )

    assert result == "get result"
    assert agents.memory.get_calls == [
        "ismim ne"
    ]


@pytest.mark.unit
def test_memory_orchestrator_missing_decision():

    agents = FakeAgents()
    orchestrator = MemoryOrchestrator(agents)

    result = orchestrator.run(
        "ismim ne"
    )

    assert result == "Memory decision missing."


@pytest.mark.unit
def test_memory_orchestrator_unknown_action():

    agents = FakeAgents()
    orchestrator = MemoryOrchestrator(agents)

    result = orchestrator.run(
        "test",
        {"action": "delete"},
    )

    assert result == "Unknown memory action."