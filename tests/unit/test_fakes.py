import pytest


@pytest.mark.unit
def test_fake_llm_is_deterministic(fake_llm):
    first = fake_llm.generate("hello")
    second = fake_llm.generate("hello")

    assert first == second
    assert first == "Fake response"


@pytest.mark.unit
def test_fake_llm_tracks_calls(fake_llm):
    fake_llm.generate("one")
    fake_llm.generate("two")

    assert fake_llm.call_count == 2
    assert fake_llm.calls == ["one", "two"]


@pytest.mark.unit
def test_fake_memory_stores_data(fake_memory):
    fake_memory.add("hello")
    fake_memory.add("world")

    assert fake_memory.get() == [
        "hello",
        "world",
    ]

    assert len(fake_memory) == 2


@pytest.mark.unit
def test_fake_memory_clear(fake_memory):
    fake_memory.add("hello")

    fake_memory.clear()

    assert fake_memory.get() == []


@pytest.mark.unit
def test_fake_tool_tracks_execution(fake_tool):
    result = fake_tool.execute(
        1,
        value="test",
    )

    assert result is None
    assert fake_tool.call_count == 1