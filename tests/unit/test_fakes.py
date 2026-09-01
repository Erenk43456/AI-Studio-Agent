import pytest

from tests.fakes.fake_code_agent import FakeCodeAgent
from tests.fakes.fake_development_context import FakeDevelopmentContext
from tests.fakes.fake_llm import FakeLLM
from tests.fakes.fake_memory import FakeMemory
from tests.fakes.fake_model_provider import FakeModelProvider
from tests.fakes.fake_project_memory import FakeProjectMemory
from tests.fakes.fake_registry import FakeRegistry
from tests.fakes.fake_repository_analyzer import FakeRepositoryAnalyzer
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

@pytest.mark.unit
def test_fake_llm_error_injection():

    llm = FakeLLM(
        error=RuntimeError("boom")
    )

    with pytest.raises(RuntimeError):
        llm.generate("test prompt")


@pytest.mark.unit
def test_fake_llm_sequential_responses():

    llm = FakeLLM(
        responses=["first", "second"]
    )

    assert llm.generate("a") == "first"
    assert llm.generate("b") == "second"


@pytest.mark.unit
def test_fake_registry_get_tracks_calls():

    registry = FakeRegistry(
        tools={"calculator": "calc-tool"}
    )

    result = registry.get("calculator")

    assert result == "calc-tool"
    assert registry.calls == ["calculator"]
    assert registry.get("missing") is None


@pytest.mark.unit
def test_fake_project_memory_read_side():

    memory = FakeProjectMemory(
        files={"a.py": "content"},
        architecture={"layer": "core"},
    )

    assert memory.get_all_files() == {"a.py": "content"}
    assert memory.get_file("a.py") == "content"
    assert memory.get_architecture() == {"layer": "core"}


@pytest.mark.unit
def test_fake_project_memory_write_side():

    memory = FakeProjectMemory()

    memory.update_project_info({"name": "AI-Studio"})
    memory.update_architecture("core", {"role": "composition"})
    result = memory.sync_repository_analysis({"overview": {}})

    assert result is True
    assert memory.calls == [
        ("project_info", {"name": "AI-Studio"}),
        ("architecture", "core", {"role": "composition"}),
        ("repository_analysis", {"overview": {}}),
    ]


@pytest.mark.unit
def test_fake_project_memory_error_injection():

    memory = FakeProjectMemory(
        error=RuntimeError("unavailable")
    )

    with pytest.raises(RuntimeError):
        memory.get_all_files()


@pytest.mark.unit
def test_fake_repository_analyzer_returns_analysis():

    analyzer = FakeRepositoryAnalyzer(
        analysis={"overview": {"python_files": 3}}
    )

    result = analyzer.analyze("/some/root")

    assert result == {"overview": {"python_files": 3}}
    assert analyzer.calls == ["/some/root"]


@pytest.mark.unit
def test_fake_code_agent_run_tracks_calls():

    agent = FakeCodeAgent(
        result={"success": True}
    )

    result = agent.run("do the thing", development_context={"x": 1})

    assert result == {"success": True}
    assert agent.calls == [("do the thing", {"x": 1})]


@pytest.mark.unit
def test_fake_development_context_build():

    context = FakeDevelopmentContext(
        context={"targets": ["a.py"]}
    )

    result = context.build("fix the bug")

    assert result == {"targets": ["a.py"]}
    assert context.calls == ["fix the bug"]
