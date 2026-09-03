import pytest

from agents.memory_agent import MemoryAgent
from tests.fakes.fake_memory import FakeMemory


@pytest.mark.unit
def test_memory_agent_extract_name_returns_name():

    agent = MemoryAgent(
        memory=FakeMemory(),
    )

    assert agent.extract_name("Benim adım Eren") == "Eren"


@pytest.mark.unit
def test_memory_agent_extract_name_ignores_name_question():

    agent = MemoryAgent(
        memory=FakeMemory(),
    )

    assert agent.extract_name("Adım ne?") is None


@pytest.mark.unit
def test_memory_agent_extract_name_returns_only_first_name_word():

    agent = MemoryAgent(
        memory=FakeMemory(),
    )

    assert (
        agent.extract_name(
            "Benim adım Eren ve bugün çalışıyorum"
        )
        == "Eren"
    )

@pytest.mark.unit
def test_memory_agent_save_handles_memory_exception():

    class FailingMemory:

        def save(self, key, value, category):
            raise RuntimeError("storage unavailable")

    agent = MemoryAgent(
        memory=FailingMemory(),
    )

    result = agent.save("Benim adım Eren")

    assert result == "Memory save error: storage unavailable"