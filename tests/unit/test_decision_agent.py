import pytest

from agents.decision_agent import DecisionAgent
from tests.fakes.fake_llm import FakeLLM


class FakeMemory:
    pass


class FakeRegistry:
    pass


@pytest.mark.unit
def test_decision_memory_get():
    agent = DecisionAgent(
        FakeLLM(),
        FakeMemory(),
        FakeRegistry(),
    )

    result = agent.process("Ben kimim?")

    assert result == {
        "system": "memory",
        "action": "get",
    }


@pytest.mark.unit
def test_decision_memory_save():
    agent = DecisionAgent(
        FakeLLM(),
        FakeMemory(),
        FakeRegistry(),
    )

    result = agent.process(
        "Benim adım Eren"
    )

    assert result == {
        "system": "memory",
        "action": "save",
    }


@pytest.mark.unit
def test_decision_calculation():
    agent = DecisionAgent(
        FakeLLM(),
        FakeMemory(),
        FakeRegistry(),
    )

    result = agent.process(
        "15 + 20 kaç eder?"
    )

    assert result["system"] == "development"


@pytest.mark.unit
def test_decision_calculation_turkish():
    agent = DecisionAgent(
        FakeLLM(),
        FakeMemory(),
        FakeRegistry(),
    )

    result = agent.process(
        "15 ile 20'yi topla"
    )

    assert result["system"] == "development"


@pytest.mark.unit
def test_decision_python_file():
    agent = DecisionAgent(
        FakeLLM(),
        FakeMemory(),
        FakeRegistry(),
    )

    result = agent.process(
        "agents/chat_agent.py dosyasını incele"
    )

    assert result["system"] == "development"


@pytest.mark.unit
def test_decision_bug_fix():
    agent = DecisionAgent(
        FakeLLM(),
        FakeMemory(),
        FakeRegistry(),
    )

    result = agent.process(
        "Bu bugı düzelt"
    )

    assert result["system"] == "development"


@pytest.mark.unit
def test_decision_file_operation():
    agent = DecisionAgent(
        FakeLLM(),
        FakeMemory(),
        FakeRegistry(),
    )

    result = agent.process(
        "agents/test.py dosyasını oluştur"
    )

    assert result["system"] == "development"


@pytest.mark.unit
def test_decision_uses_llm_for_chat():
    llm = FakeLLM(
        response={
            "system": "chat",
            "reason": "general conversation",
        }
    )

    agent = DecisionAgent(
        llm,
        FakeMemory(),
        FakeRegistry(),
    )

    result = agent.process(
        "Bugün nasılsın?"
    )

    assert result == {
        "system": "chat",
        "reason": "general conversation",
    }

    assert llm.call_count == 1


@pytest.mark.unit
def test_decision_parses_json_response():
    llm = FakeLLM(
        response='{"system": "chat", "reason": "question"}'
    )

    agent = DecisionAgent(
        llm,
        FakeMemory(),
        FakeRegistry(),
    )

    result = agent.process(
        "Python nedir?"
    )

    assert result["system"] == "chat"


@pytest.mark.unit
def test_decision_invalid_system_falls_back_to_development():
    llm = FakeLLM(
        response='{"system": "unknown"}'
    )

    agent = DecisionAgent(
        llm,
        FakeMemory(),
        FakeRegistry(),
    )

    result = agent.process(
        "Normal bir istek"
    )

    assert result["system"] == "development"


@pytest.mark.unit
def test_decision_llm_error_falls_back_to_chat():
    llm = FakeLLM()

    def failing_generate(*args, **kwargs):
        raise RuntimeError("LLM failure")

    llm.generate = failing_generate

    agent = DecisionAgent(
        llm,
        FakeMemory(),
        FakeRegistry(),
    )

    result = agent.process(
        "Merhaba"
    )

    assert result == {
        "system": "chat",
        "reason": "fallback",
    }