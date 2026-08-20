import pytest

from app.core.project_memory_sync import (
    ProjectMemorySync,
)


class FakeRepositoryAnalyzer:

    def __init__(
        self,
        analysis=None
    ):
        self.calls = []

        self.analysis = (
            analysis
            if analysis is not None
            else {
                "generated_at": (
                    "2026-08-20 21:00:00"
                ),
                "overview": {
                    "python_files": 10,
                    "total_lines": 100,
                },
                "module_roles": {},
                "definitions": {},
                "tools": [],
                "registry_names": [],
                "wiring_checks": [],
                "issues": [],
            }
        )

    def analyze(
        self,
        root
    ):
        self.calls.append(
            str(root)
        )

        return self.analysis


class FakeProjectMemory:

    def __init__(self):
        self.calls = []

    def update_project_info(
        self,
        data
    ):
        self.calls.append(
            (
                "project_info",
                data
            )
        )

    def update_architecture(
        self,
        name,
        data
    ):
        self.calls.append(
            (
                "architecture",
                name,
                data
            )
        )

    def sync_repository_analysis(
        self,
        analysis
    ):
        self.calls.append(
            (
                "repository_analysis",
                analysis
            )
        )

        return True


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
        "C:/AI-Studio",
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
def test_project_memory_sync_uses_workspace_for_repository_analysis():

    analyzer = FakeRepositoryAnalyzer()

    project_memory = FakeProjectMemory()

    sync = ProjectMemorySync(
        repository_analyzer=analyzer,
        project_memory=project_memory,
        workspace="C:/AI-Studio",
    )

    sync.sync(
        [
            "agents/chat_agent.py",
            "tools/calculator.py",
        ]
    )

    assert analyzer.calls == [
        "C:/AI-Studio"
    ]

@pytest.mark.unit
def test_project_memory_sync_stores_repository_analysis():

    analysis = {
        "generated_at": (
            "2026-08-20 21:00:00"
        ),
        "overview": {
            "python_files": 10,
            "total_lines": 100,
        },
        "module_roles": {
            "agents/chat_agent.py": (
                "Conversational agent"
            ),
        },
        "definitions": {
            "agents/chat_agent.py": [
                "class ChatAgent"
            ],
        },
        "tools": [],
        "registry_names": [],
        "wiring_checks": [],
        "issues": [],
    }

    analyzer = FakeRepositoryAnalyzer(
        analysis
    )

    project_memory = FakeProjectMemory()

    sync = ProjectMemorySync(
        repository_analyzer=analyzer,
        project_memory=project_memory,
        workspace="C:/AI-Studio",
    )

    result = sync.sync(
        [
            "agents/chat_agent.py"
        ]
    )

    assert result == analysis

    assert project_memory.calls == [
        (
            "repository_analysis",
            analysis
        )
    ]