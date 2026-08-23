import pytest

import app.core.containers.development_container as module

from app.core.containers.development_container import DevelopmentContainer
from app.core.orchestrators.development_orchestrator import DevelopmentOrchestrator


class FakeWatcher:

    def __init__(self, path, callback):
        self.path = path
        self.callback = callback
        self.started = False

    def start(self):
        self.started = True


class FakeLLM:
    pass


class FakeModels:
    code_llm = FakeLLM()
    planner_llm = FakeLLM()


class FakeProjectMemory:

    def __init__(self):
        self.calls = []

    def update_project_info(self, data):
        self.calls.append(data)


class FakeRegistry:

    def get(self, name):
        return object()


class FakeTools:
    registry = FakeRegistry()


class FakeCore:
    workspace_path = "C:/AI-Studio"


class FakeMemory:

    def __init__(self):
        self.memory = object()
        self.project_memory = FakeProjectMemory()


class FakeCodeAgent:

    def __init__(self):
        self.development_context = None


class FakeAgents:

    def __init__(self):
        self.code = FakeCodeAgent()


class FakeMain:
    core = FakeCore()
    models = FakeModels()
    tools = FakeTools()
    memory = FakeMemory()
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
