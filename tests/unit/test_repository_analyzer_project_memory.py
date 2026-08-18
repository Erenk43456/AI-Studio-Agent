import pytest

from tools.repository_analyzer import RepositoryAnalyzerTool


class FakeProjectMemory:

    def __init__(self):
        self.calls = []

    def update_project_info(self, data):
        self.calls.append(
            ("update_project_info", data)
        )

    def update_architecture(self, name, data):
        self.calls.append(
            ("update_architecture", name, data)
        )

    def add_file(self, path, data):
        self.calls.append(
            ("add_file", path, data)
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
    assert not isinstance(result, str)

@pytest.mark.unit
def test_project_memory_sync_owns_repository_analysis_result():

    from app.core.project_memory_sync import ProjectMemorySync

    class FakeRepositoryAnalyzer:

        def __init__(self):
            self.calls = []

        def execute(self, plan):
            self.calls.append(plan)

            return {
                "overview": {
                    "python_files": 10,
                },
                "modules": {},
                "definitions": {},
                "tools": [],
                "registry": [],
                "checks": [],
                "issues": [],
            }

    class FakeProjectMemory:

        def __init__(self):
            self.calls = []

        def update_project_info(self, data):
            self.calls.append(
                ("project_info", data)
            )

        def update_architecture(self, name, data):
            self.calls.append(
                ("architecture", name, data)
            )

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
        {
            "action": "analyze",
            "path": "C:/AI-Studio",
            "changed_files": [
                "agents/chat_agent.py"
            ],
        }
    ]

    assert result is not None

@pytest.mark.unit
def test_project_memory_sync_stores_repository_analysis():

    from app.core.project_memory_sync import ProjectMemorySync

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

    class FakeRepositoryAnalyzer:

        def execute(self, plan):
            return analysis

    class FakeProjectMemory:

        def __init__(self):
            self.project_info = []
            self.architecture = []

        def update_project_info(self, data):
            self.project_info.append(data)

        def update_architecture(self, name, data):
            self.architecture.append(
                (name, data)
            )

    project_memory = FakeProjectMemory()

    sync = ProjectMemorySync(
        repository_analyzer=FakeRepositoryAnalyzer(),
        project_memory=project_memory,
        workspace="C:/AI-Studio",
    )

    result = sync.sync(
        ["agents/chat_agent.py"]
    )

    assert result == analysis

    assert project_memory.architecture == [
        (
            "repository_analysis",
            analysis,
        )
    ]

@pytest.mark.unit
def test_project_memory_sync_does_not_sync_when_no_files_changed():

    from app.core.project_memory_sync import ProjectMemorySync

    class FakeRepositoryAnalyzer:

        def __init__(self):
            self.calls = []

        def execute(self, plan):
            self.calls.append(plan)
            return {}

    class FakeProjectMemory:

        def __init__(self):
            self.calls = []

        def update_architecture(self, name, data):
            self.calls.append(
                (name, data)
            )

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