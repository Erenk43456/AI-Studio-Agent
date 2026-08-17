import pytest

from app.core.containers.tool_container import ToolContainer
from tools.tool_registry import ToolRegistry


class FakeLLM:
    pass


class FakeModels:
    code_llm = FakeLLM()


class FakeMemoryStore:
    pass


class FakeProjectMemory:
    pass


class FakeMemory:

    memory = FakeMemoryStore()
    project_memory = FakeProjectMemory()


class FakeCore:
    workspace_path = "C:/AI-Studio"


@pytest.mark.unit
def test_tool_container_creates_registry():

    container = ToolContainer(
        FakeCore(),
        FakeModels(),
        FakeMemory(),
    )

    assert isinstance(
        container.registry,
        ToolRegistry,
    )


@pytest.mark.unit
def test_tool_container_registers_tools():

    container = ToolContainer(
        FakeCore(),
        FakeModels(),
        FakeMemory(),
    )

    expected_tools = {
        "calculator",
        "file",
        "code_writer",
        "code_analyzer",
        "code_repair",
        "repository_analyzer",
        "project_memory",
        "memory",
        "formatter",
    }

    for name in expected_tools:
        assert container.registry.get(name) is not None


@pytest.mark.unit
def test_tool_container_exposes_tools():

    container = ToolContainer(
        FakeCore(),
        FakeModels(),
        FakeMemory(),
    )

    assert container.calculator is not None
    assert container.file_tool is not None
    assert container.code_writer is not None
    assert container.code_analyzer is not None
    assert container.code_repair is not None
    assert container.repository_analyzer is not None
    assert container.project_memory is not None
    assert container.memory_tool is not None
    assert container.formatter is not None