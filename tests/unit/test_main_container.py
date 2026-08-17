import pytest

from app.core.containers.main_container import MainContainer
from app.core.orchestrators.main_orchestrator import MainOrchestrator
from app.core.orchestrators.memory_orchestrator import MemoryOrchestrator


@pytest.mark.unit
def test_main_container_builds():

    container = MainContainer()

    assert container.core is not None
    assert container.models is not None
    assert container.memory is not None
    assert container.tools is not None
    assert container.agents is not None
    assert container.chat is not None
    assert container.development is not None


@pytest.mark.unit
def test_main_container_wires_orchestrators():

    container = MainContainer()

    assert isinstance(
        container.orchestrator,
        MainOrchestrator,
    )

    assert isinstance(
        container.memory.orchestrator,
        MemoryOrchestrator,
    )


@pytest.mark.unit
def test_main_container_wires_systems():

    container = MainContainer()

    assert (
        container.orchestrator.systems["chat"]
        is container.chat.orchestrator
    )

    assert (
        container.orchestrator.systems["memory"]
        is container.memory.orchestrator
    )

    assert (
        container.orchestrator.systems["development"]
        is container.development.orchestrator
    )


@pytest.mark.unit
def test_main_container_agents_use_main_container():

    container = MainContainer()

    assert container.agents is not None