import pytest

from app.core.orchestrators.main_orchestrator import MainOrchestrator
from tests.fakes.fake_llm import FakeLLM

class FakeOrchestrator:

    def __init__(self, result):
        self.result = result
        self.calls = []

    def run(
        self,
        message,
        decision,
        conversation=None,
        execution=None,
    ):
        self.calls.append(
            (
                message,
                decision,
                conversation,
                execution,
            )
        )
        return self.result


class FakeDecisionAgent:

    def __init__(self, decision):
        self.decision = decision
        self.calls = []

    def process(self, message):
        self.calls.append(message)
        return self.decision


class FakeContainer:

    def __init__(self, decision):

        self.models = type(
            "Models",
            (),
            {
                "decision_llm": FakeLLM()
            }
        )

        self.agents = type(
            "Agents",
            (),
            {
                "decision": FakeDecisionAgent(
                    decision
                )
            }
        )()

        self.chat = type(
            "Chat",
            (),
            {
                "orchestrator": FakeOrchestrator(
                    "chat result"
                )
            }
        )()

        self.memory = type(
            "Memory",
            (),
            {
                "orchestrator": FakeOrchestrator(
                    "memory result"
                )
            }
        )()

        self.development = type(
            "Development",
            (),
            {
                "orchestrator": FakeOrchestrator(
                    "development result"
                )
            }
        )()


@pytest.mark.unit
def test_main_orchestrator_routes_to_chat():

    container = FakeContainer(
        {"system": "chat"}
    )

    orchestrator = MainOrchestrator(
        container
    )

    result = orchestrator.run(
        "hello",
        "conversation"
    )

    assert result == "chat result"

    assert len(
        container.chat.orchestrator.calls
    ) == 1

    message, decision, conversation, execution = (
        container.chat.orchestrator.calls[0]
    )

    assert message == "hello"
    assert decision == {"system": "chat"}
    assert conversation == "conversation"

    assert execution is not None
    assert "agents" in execution
    assert "models" in execution


@pytest.mark.unit
def test_main_orchestrator_routes_to_memory():

    container = FakeContainer(
        {"system": "memory"}
    )

    orchestrator = MainOrchestrator(
        container
    )

    result = orchestrator.run(
        "my name is Eren"
    )

    assert result == "memory result"

    assert (
        len(
            container.memory.orchestrator.calls
        )
        == 1
    )


@pytest.mark.unit
def test_main_orchestrator_routes_to_development():

    container = FakeContainer(
        {"system": "development"}
    )

    orchestrator = MainOrchestrator(
        container
    )

    result = orchestrator.run(
        "fix the project"
    )

    assert result == "development result"


@pytest.mark.unit
def test_main_orchestrator_defaults_to_chat():

    container = FakeContainer({})

    orchestrator = MainOrchestrator(
        container
    )

    result = orchestrator.run(
        "hello"
    )

    assert result == "chat result"


@pytest.mark.unit
def test_main_orchestrator_unknown_system():

    container = FakeContainer(
        {"system": "unknown"}
    )

    orchestrator = MainOrchestrator(
        container
    )

    result = orchestrator.run(
        "test"
    )

    assert result == {
        "error": "Unknown system: unknown"
    }


@pytest.mark.unit
def test_main_orchestrator_calls_decision_agent():

    container = FakeContainer(
        {"system": "chat"}
    )

    orchestrator = MainOrchestrator(
        container
    )

    orchestrator.run(
        "hello"
    )

    assert (
        container.agents.decision.calls
        == ["hello"]
    )