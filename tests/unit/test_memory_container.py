import pytest

from app.core.containers.memory_container import MemoryContainer
from app.core.orchestrators.memory_orchestrator import MemoryOrchestrator


class FakeCore:
    workspace_path = "C:/AI-Studio"


class FakeAgents:
    memory = object()


@pytest.mark.unit
def test_memory_container_creates_components():

    container = MemoryContainer(
        FakeCore()
    )

    assert container.memory is not None
    assert container.chat_manager is not None
    assert container.project_memory is not None
    assert container.orchestrator is None


@pytest.mark.unit
def test_memory_container_attaches_agents():

    container = MemoryContainer(
        FakeCore()
    )

    container.attach_agents(
        FakeAgents()
    )

    assert isinstance(
        container.orchestrator,
        MemoryOrchestrator,
    )