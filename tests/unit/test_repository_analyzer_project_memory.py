import pytest

from pathlib import Path

from app.core.project_memory_sync import (
    ProjectMemorySync,
)
from tests.fakes.fake_project_memory import FakeProjectMemory
from tests.fakes.fake_repository_analyzer import FakeRepositoryAnalyzer
from tools.repository_analyzer import (
    RepositoryAnalyzerTool,
)


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
        str(Path("C:/AI-Studio"))
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
        str(Path("C:/AI-Studio"))
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