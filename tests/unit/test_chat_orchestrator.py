import pytest

from app.core.orchestrators.chat_orchestrator import (
    ChatOrchestrator,
)


class FakeChatAgent:

    def __init__(self):
        self.conversation = None
        self.calls = []

    def chat(self, message):
        self.calls.append(message)
        return "chat result"


class FakeContainer:

    def __init__(self):
        self.chat_agent = FakeChatAgent()


@pytest.mark.unit
def test_chat_orchestrator_runs_chat():

    container = FakeContainer()
    orchestrator = ChatOrchestrator(container)

    result = orchestrator.run(
        "hello"
    )

    assert result == "chat result"

    assert container.chat_agent.calls == [
        "hello"
    ]


@pytest.mark.unit
def test_chat_orchestrator_sets_conversation():

    container = FakeContainer()
    orchestrator = ChatOrchestrator(container)

    conversation = [
        {"role": "user", "content": "hello"}
    ]

    orchestrator.run(
        "how are you?",
        conversation=conversation,
    )

    assert (
        container.chat_agent.conversation
        == conversation
    )

    assert container.chat_agent.calls == [
        "how are you?"
    ]