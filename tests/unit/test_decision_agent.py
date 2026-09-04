import pytest

from agents.decision_agent import DecisionAgent
from agents.contracts.decision import DecisionContract
from tests.fakes.fake_llm import FakeLLM
from tests.fakes.fake_memory import FakeMemory
from tests.fakes.fake_registry import FakeRegistry


@pytest.mark.unit
def test_decision_memory_get():
    agent = DecisionAgent(
        FakeLLM(),
        FakeMemory(),
        FakeRegistry(),
    )

    result = agent.process("Ben kimim?")

    assert isinstance(result, DecisionContract)
    assert result.system == "memory"
    assert result.action == "get"


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

    assert isinstance(result, DecisionContract)
    assert result.system == "memory"
    assert result.action == "save"


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

    assert isinstance(result, DecisionContract)
    assert result.system == "development"


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

    assert isinstance(result, DecisionContract)
    assert result.system == "development"


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

    assert isinstance(result, DecisionContract)
    assert result.system == "development"


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

    assert isinstance(result, DecisionContract)
    assert result.system == "development"


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

    assert isinstance(result, DecisionContract)
    assert result.system == "development"


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

    assert isinstance(result, DecisionContract)
    assert result.system == "chat"
    assert result.reason == "general conversation"
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

    assert isinstance(result, DecisionContract)
    assert result.system == "chat"


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

    assert isinstance(result, DecisionContract)
    assert result.system == "development"


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

    assert isinstance(result, DecisionContract)
    assert result.system == "chat"
    assert result.reason == "fallback"

@pytest.mark.unit
def test_decision_repository_analysis():
    agent = DecisionAgent(
        FakeLLM(),
        FakeMemory(),
        FakeRegistry(),
    )

    result = agent.process(
        "Bu repository'yi analiz et"
    )

    assert isinstance(result, DecisionContract)
    assert result.system == "development"
    assert result.action == "analyze"


@pytest.mark.unit
def test_decision_file_inspection():
    agent = DecisionAgent(
        FakeLLM(),
        FakeMemory(),
        FakeRegistry(),
    )

    result = agent.process(
        "agents/chat_agent.py dosyasını incele"
    )

    assert isinstance(result, DecisionContract)
    assert result.system == "development"
    assert result.action == "analyze"


@pytest.mark.unit
def test_decision_bug_fix_routes_to_code():
    agent = DecisionAgent(
        FakeLLM(),
        FakeMemory(),
        FakeRegistry(),
    )

    result = agent.process(
        "Bu bugı düzelt"
    )

    assert isinstance(result, DecisionContract)
    assert result.system == "development"
    assert result.action == "code"


@pytest.mark.unit
def test_decision_refactor_routes_to_improve():
    agent = DecisionAgent(
        FakeLLM(),
        FakeMemory(),
        FakeRegistry(),
    )

    result = agent.process(
        "Bu kodu refactor et"
    )

    assert isinstance(result, DecisionContract)
    assert result.system == "development"
    assert result.action == "improve"

@pytest.mark.unit
def test_process_extracts_first_json_object_from_extra_response_content():
    class FakeLLM:
        def generate(self, prompt, temperature=0.1):
            return (
                'Here is the decision:\n'
                '{"system": "development", "reason": "code request"}\n'
                'Additional data: {"ignored": true}'
            )

    agent = DecisionAgent(
        llm=FakeLLM(),
        memory=None,
        registry=None,
    )

    result = agent.process(
        "Bana uygun bir sistem seç."
    )

    assert result.system == "development"
    assert result.reason == "code request"