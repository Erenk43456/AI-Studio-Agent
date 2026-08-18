import pytest

from app.core.project_memory_sync import (
    ProjectMemorySync,
)


class FakeRepositoryAnalyzer:

    def __init__(self):
        self.calls = []

    def execute(self, plan):
        self.calls.append(plan)

        return "analysis complete"


class FakeProjectMemory:

    def __init__(self):
        self.calls = []

    def update_project_info(self, data):
        self.calls.append(data)


@pytest.mark.unit
def test_project_memory_sync_accepts_changed_files():

    analyzer = FakeRepositoryAnalyzer()
    project_memory = FakeProjectMemory()

    sync = ProjectMemorySync(
        repository_analyzer=analyzer,
        project_memory=project_memory,
        workspace="C:/AI-Studio",
    )

    assert sync.workspace == "C:/AI-Studio"
    assert sync.repository_analyzer is analyzer
    assert sync.project_memory is project_memory

@pytest.mark.unit
def test_project_memory_sync_runs_repository_analysis():

    analyzer = FakeRepositoryAnalyzer()
    project_memory = FakeProjectMemory()

    sync = ProjectMemorySync(
        repository_analyzer=analyzer,
        project_memory=project_memory,
        workspace="C:/AI-Studio",
    )

    changed_files = [
        "agents/chat_agent.py",
    ]

    sync.sync(
        changed_files
    )

    assert analyzer.calls == [
        {
            "action": "analyze",
            "path": "C:/AI-Studio",
            "changed_files": changed_files,
        }
    ]

@pytest.mark.unit
def test_project_memory_sync_does_not_analyze_without_changes():

    analyzer = FakeRepositoryAnalyzer()
    project_memory = FakeProjectMemory()

    sync = ProjectMemorySync(
        repository_analyzer=analyzer,
        project_memory=project_memory,
        workspace="C:/AI-Studio",
    )

    result = sync.sync([])

    assert result is None
    assert analyzer.calls == []

class FailingRepositoryAnalyzer:

    def execute(self, plan):
        raise RuntimeError(
            "repository analysis failed"
        )


@pytest.mark.unit
def test_project_memory_sync_handles_analysis_failure():

    analyzer = FailingRepositoryAnalyzer()
    project_memory = FakeProjectMemory()

    sync = ProjectMemorySync(
        repository_analyzer=analyzer,
        project_memory=project_memory,
        workspace="C:/AI-Studio",
    )

    result = sync.sync(
        ["agents/chat_agent.py"]
    )

    assert result is None

@pytest.mark.unit
def test_project_memory_sync_passes_changed_files_to_repository_analyzer():
    analyzer = FakeRepositoryAnalyzer()
    project_memory = FakeProjectMemory()

    sync = ProjectMemorySync(
        repository_analyzer=analyzer,
        project_memory=project_memory,
        workspace="C:/AI-Studio",
    )

    changed_files = [
        "agents/chat_agent.py",
        "tools/calculator.py",
    ]

    sync.sync(changed_files)

    assert analyzer.calls[-1] == {
        "action": "analyze",
        "path": "C:/AI-Studio",
        "changed_files": changed_files,
    }