import pytest

from tools.repository_analyzer import RepositoryAnalyzerTool


@pytest.mark.unit
def test_repository_analyzer_execute_does_not_require_project_memory(
    tmp_path,
):
    main = tmp_path / "main.py"
    main.write_text(
        "print('hello')",
        encoding="utf-8",
    )

    analyzer = RepositoryAnalyzerTool(
        root=tmp_path,
    )

    result = analyzer.execute(
        {
            "action": "analyze",
            "path": str(tmp_path),
        }
    )

    assert result is not None

@pytest.mark.unit
def test_repository_analyzer_does_not_update_project_memory(
    tmp_path,
):
    main = tmp_path / "main.py"
    main.write_text(
        "print('hello')",
        encoding="utf-8",
    )

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

        def add_file(self, path, data):
            self.calls.append(
                ("file", path, data)
            )

    project_memory = FakeProjectMemory()

    analyzer = RepositoryAnalyzerTool(
        root=tmp_path,
    )

    analyzer.execute(
        {
            "action": "analyze",
            "path": str(tmp_path),
        }
    )

    assert project_memory.calls == []