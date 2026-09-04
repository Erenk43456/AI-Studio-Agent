import pytest

import app.core.containers.development_container as module

from app.core.containers.development_container import DevelopmentContainer
from app.core.orchestrators.development_orchestrator import DevelopmentOrchestrator
from tests.fakes.fake_code_agent import FakeCodeAgent
from tests.fakes.fake_llm import FakeLLM
from tests.fakes.fake_memory import FakeMemory
from tests.fakes.fake_project_memory import FakeProjectMemory
from tests.fakes.fake_registry import FakeRegistry
from tests.fakes.fake_repository_analyzer import FakeRepositoryAnalyzer


class FakeWatcher:

    def __init__(self, path, callback):
        self.path = path
        self.callback = callback
        self.started = False
        self.stopped = False

    def start(self):
        self.started = True

    def stop(self):
        self.stopped = True

class FakeModels:
    code_llm = FakeLLM()
    planner_llm = FakeLLM()


class FakeTools:
    registry = FakeRegistry(
        tools={"repository_analyzer": FakeRepositoryAnalyzer()}
    )


class FakeCore:
    workspace_path = "C:/AI-Studio"


class FakeAgents:

    def __init__(self):
        self.code = FakeCodeAgent()


class FakeMemoryContainer:
    """
    Container-shaped double: DevelopmentContainer expects a memory
    *container* here (with .memory and .project_memory attributes),
    not a Memory implementation itself.
    """

    memory = FakeMemory()
    project_memory = FakeProjectMemory()


class FakeMain:
    core = FakeCore()
    models = FakeModels()
    tools = FakeTools()
    memory = FakeMemoryContainer()
    agents = FakeAgents()


@pytest.mark.unit
def test_development_container_creates_components(monkeypatch):

    monkeypatch.setattr(module, "WorkspaceWatcher", FakeWatcher)

    container = DevelopmentContainer(FakeMain())

    assert container.planner is not None
    assert container.code_agent is not None
    assert container.development_context is not None
    assert container.repository_analyzer is not None
    assert container.watcher.started is True

    assert isinstance(container.orchestrator, DevelopmentOrchestrator)


@pytest.mark.unit
def test_development_container_uses_shared_dependencies(monkeypatch):

    monkeypatch.setattr(module, "WorkspaceWatcher", FakeWatcher)

    main = FakeMain()

    container = DevelopmentContainer(main)

    assert container.workspace_path == (main.core.workspace_path)

    assert container.registry is (main.tools.registry)

    assert container.project_memory is (main.memory.project_memory)

    assert container.code_llm is (main.models.code_llm)

    assert container.planner_llm is (main.models.planner_llm)

    assert container.planner.registry is (main.tools.registry)

    assert container.tool_agent.registry is (main.tools.registry)

    assert container.tool_agent.code_agent is (container.code_agent)


@pytest.mark.unit
def test_workspace_changes_trigger_project_memory_sync(monkeypatch):

    monkeypatch.setattr(module, "WorkspaceWatcher", FakeWatcher)

    class FakeProjectMemorySync:

        instances = []

        def __init__(self, repository_analyzer, project_memory, workspace):
            self.repository_analyzer = repository_analyzer
            self.project_memory = project_memory
            self.workspace = workspace
            self.calls = []

            FakeProjectMemorySync.instances.append(self)

        def sync(self, changed_files):
            self.calls.append(changed_files)

    monkeypatch.setattr(module, "ProjectMemorySync", FakeProjectMemorySync)

    main = FakeMain()

    container = DevelopmentContainer(main)

    changed_files = [
        "agents/chat_agent.py",
    ]

    container.on_workspace_changes(changed_files)

    sync = FakeProjectMemorySync.instances[-1]

    assert sync.calls == [changed_files]

@pytest.mark.unit
def test_development_container_close_stops_watcher(monkeypatch):

    monkeypatch.setattr(module, "WorkspaceWatcher", FakeWatcher)

    container = DevelopmentContainer(FakeMain())

    assert container.watcher.started is True
    assert container.watcher.stopped is False

    container.close()

    assert container.watcher.stopped is True

@pytest.mark.unit
def test_development_container_context_manager_closes_watcher(monkeypatch):

    monkeypatch.setattr(module, "WorkspaceWatcher", FakeWatcher)

    with DevelopmentContainer(FakeMain()) as container:
        assert container.watcher.started is True

    assert container.watcher.stopped is True