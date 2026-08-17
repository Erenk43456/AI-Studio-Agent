import pytest

from tests.fakes.fake_llm import FakeLLM
from tests.fakes.fake_memory import FakeMemory
from tests.fakes.fake_model_provider import FakeModelProvider
from tests.fakes.fake_tool import FakeTool


@pytest.mark.unit
def test_fake_llm_generate():

    llm = FakeLLM(
        response="hello"
    )

    result = llm.generate(
        "test prompt"
    )

    assert result == "hello"
    assert llm.call_count == 1


@pytest.mark.unit
def test_fake_llm_tracks_prompts():

    llm = FakeLLM()

    llm.generate("first")
    llm.generate("second")

    assert llm.calls == [
        "first",
        "second",
    ]


@pytest.mark.unit
def test_fake_memory_stores_data():

    memory = FakeMemory()

    memory.save(
        "test-key",
        "hello",
    )

    assert memory.get(
        "test-key"
    ) == "hello"


@pytest.mark.unit
def test_fake_memory_clear():

    memory = FakeMemory()

    memory.save(
        "test-key",
        "hello",
    )

    memory.clear()

    assert memory.recall() == {}


@pytest.mark.unit
def test_fake_tool_tracks_execution():

    tool = FakeTool(
        result="success"
    )

    result = tool.execute(
        1,
        value="test",
    )

    assert result == "success"
    assert tool.call_count == 1

    assert tool.calls[0]["args"] == (
        1,
    )

    assert tool.calls[0]["kwargs"] == {
        "value": "test"
    }