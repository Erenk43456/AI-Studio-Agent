import pytest

from app.core.project_memory_sync import (
    ProjectMemorySync,
)
from tools.repository_analyzer import (
    RepositoryAnalyzerTool,
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
                "overview": {
                    "python_files": 10,
                },
                "modules": {},
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
                data,
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
                data,
            )
        )

    def add_file(
        self,
        path,
        data
    ):
        self.calls.append(
            (
                "file",
                path,
                data,
            )
        )

    def sync_repository_analysis(
        self,
        analysis
    ):
        self.calls.append(
            (
                "repository_analysis",
                analysis,
            )
        )

        return True


@pytest.mark.unit
def test_repository_analyzer_can_analyze_without_project_memory(
    tmp_path
):
    main_file = tmp_path / "main.py"

    main_file.write_text(
        "print('hello')",
        encoding="utf-8",
    )

    analyzer = RepositoryAnalyzerTool(
        root=tmp_path
    )

    result = analyzer.analyze(
        tmp_path
    )

    assert result is not None
    assert not isinstance(
        result,
        str
    )


@pytest.mark.unit
def test_project_memory_sync_owns_repository_analysis_result():

    analyzer = FakeRepositoryAnalyzer()

    project_memory = FakeProjectMemory()

    sync = ProjectMemorySync(
        repository_analyzer=analyzer,
        project_memory=project_memory,
        workspace="C:/AI-Studio",
    )

    result = sync.sync(
        ["agents/chat_agent.py"]
    )

    assert analyzer.calls == [
        "C:/AI-Studio"
    ]

    assert result is not None

    assert project_memory.calls == [
        (
            "repository_analysis",
            analyzer.analysis,
        )
    ]


@pytest.mark.unit
def test_project_memory_sync_stores_repository_analysis():

    analysis = {
        "overview": {
            "python_files": 10,
        },
        "modules": {
            "app/core": "Core modules",
        },
        "definitions": {
            "agents/chat_agent.py": [
                "class ChatAgent"
            ],
        },
        "tools": [
            {
                "file": "tools/calculator.py",
                "has_execute": True,
            },
        ],
        "registry": [
            "calculator",
        ],
        "checks": [
            {
                "label": "Tool registry",
                "ok": True,
            },
        ],
        "issues": [],
    }

    analyzer = FakeRepositoryAnalyzer(
        analysis=analysis
    )

    project_memory = FakeProjectMemory()

    sync = ProjectMemorySync(
        repository_analyzer=analyzer,
        project_memory=project_memory,
        workspace="C:/AI-Studio",
    )

    result = sync.sync(
        ["agents/chat_agent.py"]
    )

    assert result == analysis

    assert analyzer.calls == [
        "C:/AI-Studio"
    ]

    assert project_memory.calls == [
        (
            "repository_analysis",
            analysis,
        )
    ]


@pytest.mark.unit
def test_project_memory_sync_does_not_sync_when_no_files_changed():

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
    assert project_memory.calls == []