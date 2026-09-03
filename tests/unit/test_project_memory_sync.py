import pytest

from pathlib import Path

from app.core.project_memory_sync import (
    ProjectMemorySync,
)
from memory.project_memory.project_memory import ProjectMemory
from tests.fakes.fake_project_memory import FakeProjectMemory
from tests.fakes.fake_repository_analyzer import FakeRepositoryAnalyzer


@pytest.mark.unit
def test_project_memory_sync_accepts_changed_files():

    analyzer = FakeRepositoryAnalyzer()
    project_memory = FakeProjectMemory()

    sync = ProjectMemorySync(
        repository_analyzer=analyzer,
        project_memory=project_memory,
        workspace="C:/AI-Studio",
    )

    assert sync.workspace == Path("C:/AI-Studio")
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

    sync.sync(changed_files)

    assert analyzer.calls == [
        str(Path("C:/AI-Studio")),
    ]

    assert sync.last_changed_files == changed_files
    assert sync.last_sync_mode == "full_rescan_fallback"


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


@pytest.mark.unit
def test_project_memory_sync_incrementally_updates_modified_python_file(tmp_path):
    path = tmp_path / "keep.py"
    path.write_text("def keep():\n    return True\n", encoding="utf-8")
    memory = IncrementalMemory(tmp_path)
    analyzer = FallbackAnalyzer(None)
    sync = ProjectMemorySync(analyzer, memory, tmp_path)
    sync.indexer = FakeIncrementalIndexer()
    sync.python_analyzer = FakeIncrementalPythonAnalyzer()

    result = sync.sync([str(path)])

    assert analyzer.calls == []
    assert result["files"]["keep.py"]["content_hash"] == "sha256:keep.py"
    assert result["definitions"]["keep.py"] == ["def keep("]
    assert sync.python_analyzer.calls == [(str(path), str(tmp_path))]


@pytest.mark.unit
def test_project_memory_sync_adds_python_file(tmp_path):
    path = tmp_path / "new.py"
    path.write_text("def new():\n    pass\n", encoding="utf-8")
    memory = IncrementalMemory(tmp_path)
    sync = ProjectMemorySync(FallbackAnalyzer(None), memory, tmp_path)
    sync.indexer = FakeIncrementalIndexer()
    sync.python_analyzer = FakeIncrementalPythonAnalyzer()

    result = sync.sync(["new.py"])

    assert "new.py" in result["files"]
    assert "new.py" in result["symbols"]
    assert "new.py" in result["dependencies"]


@pytest.mark.unit
def test_project_memory_sync_adds_non_python_without_python_analysis(tmp_path):
    path = tmp_path / "new.ts"
    path.write_text("export const value = 1;\n", encoding="utf-8")
    memory = IncrementalMemory(tmp_path)
    sync = ProjectMemorySync(FallbackAnalyzer(None), memory, tmp_path)
    sync.indexer = FakeIncrementalIndexer()
    sync.python_analyzer = FakeIncrementalPythonAnalyzer()

    result = sync.sync([str(path)])

    assert result["files"]["new.ts"]["language"] == "typescript"
    assert "new.ts" not in result["symbols"]
    assert sync.python_analyzer.calls == []


@pytest.mark.unit
def test_project_memory_sync_removes_deleted_file_records_and_stale_relationships(
    tmp_path,
):
    memory = IncrementalMemory(tmp_path)
    sync = ProjectMemorySync(FallbackAnalyzer(None), memory, tmp_path)
    sync.indexer = FakeIncrementalIndexer()
    sync.python_analyzer = FakeIncrementalPythonAnalyzer()

    result = sync.sync([str(tmp_path / "old.py")])

    assert "old.py" not in result["files"]
    assert "old.py" not in result["symbols"]
    assert "old.py" not in result["dependencies"]
    assert "old.py" not in result["definitions"]

    assert result["relationships"] == []


@pytest.mark.unit
def test_project_memory_sync_normalizes_deduplicates_and_sorts_changed_paths(tmp_path):
    for filename in ("a.py", "b.py"):
        (tmp_path / filename).write_text("x\n", encoding="utf-8")
    memory = IncrementalMemory(tmp_path)
    sync = ProjectMemorySync(FallbackAnalyzer(None), memory, tmp_path)
    sync.indexer = FakeIncrementalIndexer()
    sync.python_analyzer = FakeIncrementalPythonAnalyzer()

    sync.sync([str(tmp_path / "b.py"), "a.py", str(tmp_path / "a.py")])

    assert sync.last_changed_files == ["a.py", "b.py"]
    assert [call[1] for call in sync.indexer.calls] == ["a.py", "b.py"]


@pytest.mark.unit
def test_project_memory_sync_uses_full_fallback_for_outside_path(tmp_path):
    fallback_result = {"generated_at": "fallback"}
    analyzer = FallbackAnalyzer(fallback_result)
    memory = IncrementalMemory(tmp_path)
    sync = ProjectMemorySync(analyzer, memory, tmp_path)

    result = sync.sync([str(tmp_path.parent / "outside.py")])

    assert result == fallback_result
    assert analyzer.calls == [str(tmp_path)]
    assert sync.last_sync_mode == "full_rescan_fallback"


@pytest.mark.unit
def test_project_memory_sync_invalid_snapshot_uses_full_fallback(tmp_path):
    fallback_result = {"generated_at": "fallback"}
    analyzer = FallbackAnalyzer(fallback_result)
    memory = IncrementalMemory(tmp_path)
    memory.has_valid_repository_snapshot = lambda: False
    sync = ProjectMemorySync(analyzer, memory, tmp_path)

    assert sync.sync(["keep.py"]) == fallback_result
    assert analyzer.calls == [str(tmp_path)]


@pytest.mark.unit
def test_project_memory_sync_incremental_path_does_not_call_full_analyzer(tmp_path):
    memory = IncrementalMemory(tmp_path)
    analyzer = FallbackAnalyzer(None)
    sync = ProjectMemorySync(analyzer, memory, tmp_path)
    sync.indexer = FakeIncrementalIndexer()
    sync.python_analyzer = FakeIncrementalPythonAnalyzer()

    sync.sync(["keep.py"])

    assert analyzer.calls == []


@pytest.mark.unit
def test_project_memory_sync_persists_complete_snapshot_and_recomputes_identity(
    tmp_path,
):
    (tmp_path / "keep.py").write_text("keep\n", encoding="utf-8")
    memory = IncrementalMemory(tmp_path)
    sync = ProjectMemorySync(FallbackAnalyzer(None), memory, tmp_path)
    sync.indexer = FakeIncrementalIndexer()
    sync.python_analyzer = FakeIncrementalPythonAnalyzer()

    result = sync.sync(["keep.py"])
    persisted = memory.sync_calls[0]

    assert set(result["files"]) == {"keep.py", "old.py"}
    assert persisted["metadata"]["total_files"] == 2
    assert persisted["repository_fingerprint"].startswith("sha256:")
    assert persisted["generation_id"]


@pytest.mark.unit
def test_project_memory_sync_fallback_success_is_ready_capable(tmp_path):
    fallback_result = {
        "generated_at": "fallback",
        "files": {},
        "overview": {},
        "definitions": {},
        "module_roles": {},
    }
    analyzer = FallbackAnalyzer(fallback_result)
    memory = IncrementalMemory(tmp_path)
    memory.has_valid_repository_snapshot = lambda: False
    sync = ProjectMemorySync(analyzer, memory, tmp_path)

    result = sync.sync(["keep.py"])

    assert result == fallback_result
    assert memory.sync_calls == [fallback_result]


@pytest.mark.unit
def test_project_memory_sync_persistence_failure_falls_back(tmp_path):
    (tmp_path / "keep.py").write_text("keep\n", encoding="utf-8")
    fallback_result = {"generated_at": "fallback"}
    analyzer = FallbackAnalyzer(fallback_result)
    memory = IncrementalMemory(tmp_path, sync_result=False)
    original_sync = memory.sync_repository_analysis

    def fail_incremental_then_accept_fallback(analysis):
        if len(memory.sync_calls) == 0:
            memory.sync_calls.append(analysis)
            return False
        memory.sync_calls.append(analysis)
        return True

    memory.sync_repository_analysis = fail_incremental_then_accept_fallback
    sync = ProjectMemorySync(analyzer, memory, tmp_path)
    sync.indexer = FakeIncrementalIndexer()
    sync.python_analyzer = FakeIncrementalPythonAnalyzer()

    result = sync.sync(["keep.py"])

    assert result == fallback_result
    assert analyzer.calls == [str(tmp_path)]


class IncrementalMemory:
    def __init__(self, workspace, sync_result=True):
        self.workspace = Path(workspace)
        self.sync_result = sync_result
        self.sync_calls = []
        self.files = {
            "keep.py": {
                "language": "python",
                "extension": ".py",
                "size_bytes": 1,
                "line_count": 1,
                "content_hash": "sha256:keep",
            },
            "old.py": {
                "language": "python",
                "extension": ".py",
                "size_bytes": 1,
                "line_count": 1,
                "content_hash": "sha256:old",
            },
        }
        self.symbols = {"keep.py": [{"name": "keep"}], "old.py": [{"name": "old"}]}
        self.dependencies = {"keep.py": [{"target": "old.py", "kind": "import"}]}
        self.relationships = {
            "edges": [{"source": "keep.py", "target": "old.py", "kind": "uses"}]
        }
        self.architecture = {
            "generation_id": "old-generation",
            "repository_analysis": {
                "generated_at": "2026-08-24 12:00:00",
                "overview": {},
                "files": self.files,
                "symbols": self.symbols,
                "dependencies": self.dependencies,
                "relationships": self.relationships["edges"],
                "definitions": {"keep.py": ["def keep("]},
                "module_roles": {},
            },
        }

    def has_valid_repository_snapshot(self):
        return True

    def get_architecture(self):
        return self.architecture

    def get_all_files(self):
        return self.files

    def get_symbols(self):
        return self.symbols

    def get_dependencies(self):
        return self.dependencies

    def get_relationships(self):
        return self.relationships

    def sync_repository_analysis(self, analysis):
        self.sync_calls.append(analysis)
        return self.sync_result

    def set_analysis_state(self, state):
        self.state = state


class FakeIncrementalIndexer:
    def __init__(self):
        self.calls = []

    def file_metadata(self, path, relative_path):
        self.calls.append((str(path), relative_path))
        return {
            "path": relative_path,
            "language": "python" if relative_path.endswith(".py") else "typescript",
            "extension": Path(relative_path).suffix,
            "size_bytes": 10,
            "line_count": 2,
            "content_hash": f"sha256:{relative_path}",
            "is_binary": False,
        }


class FakeIncrementalPythonAnalyzer:
    def __init__(self):
        self.calls = []

    def analyze_file(self, path, root):
        self.calls.append((str(path), str(root)))
        return {
            "symbols": [{"name": Path(path).stem}],
            "dependencies": [{"source": Path(path).name, "target": "keep.py"}],
            "definitions": [f"def {Path(path).stem}("],
        }


class FallbackAnalyzer:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def analyze(self, root):
        self.calls.append(str(root))
        return self.result


@pytest.mark.unit
def test_project_memory_sync_handles_analysis_failure():

    analyzer = FakeRepositoryAnalyzer(error=RuntimeError("repository analysis failed"))
    project_memory = FakeProjectMemory()

    sync = ProjectMemorySync(
        repository_analyzer=analyzer,
        project_memory=project_memory,
        workspace="C:/AI-Studio",
    )

    result = sync.sync(["agents/chat_agent.py"])

    assert result is None


@pytest.mark.unit
def test_project_memory_sync_initializes_empty_repository_memory(tmp_path):
    analyzer = FakeRepositoryAnalyzer(
        analysis={
            "schema_version": 2,
            "repository_root": str(tmp_path.resolve()),
            "repository_fingerprint": "sha256:fingerprint",
            "generation_id": "generation-1",
            "generated_at": "2026-08-24 12:00:00",
            "overview": {},
            "files": {
                "app.py": {
                    "language": "python",
                    "content_hash": "sha256:file",
                },
            },
            "symbols": {"app.py": []},
            "dependencies": {"app.py": []},
            "relationships": [],
            "definitions": {},
            "module_roles": {},
        }
    )
    memory = ProjectMemory(tmp_path)
    sync = ProjectMemorySync(analyzer, memory, tmp_path)

    result = sync.initialize()

    assert result is not None
    assert memory.has_valid_repository_snapshot() is True
    assert memory.get_analysis_state()["generation_id"] == "generation-1"
    assert memory.get_all_files()["app.py"]["language"] == "python"
    assert sync.last_sync_mode == "initial_full_scan"


@pytest.mark.unit
def test_project_memory_sync_does_not_reinitialize_valid_snapshot(tmp_path):
    memory = ProjectMemory(tmp_path)
    memory.set_analysis_state(
        {
            "status": "ready",
            "generation_id": "generation-1",
            "repository_fingerprint": "sha256:fingerprint",
            "files_indexed": 1,
            "store_generations": {
                name: "generation-1"
                for name in (
                    "project",
                    "files",
                    "symbols",
                    "dependencies",
                    "relationships",
                    "architecture",
                )
            },
        }
    )
    analyzer = FakeRepositoryAnalyzer()
    sync = ProjectMemorySync(analyzer, memory, tmp_path)

    result = sync.initialize()

    assert result["generation_id"] == "generation-1"
    assert analyzer.calls == []


@pytest.mark.unit
def test_project_memory_sync_initialization_failure_is_not_ready(tmp_path):
    memory = ProjectMemory(tmp_path)
    sync = ProjectMemorySync(
        FakeRepositoryAnalyzer(error=RuntimeError("repository analysis failed")),
        memory,
        tmp_path,
    )

    result = sync.initialize()

    assert result is None
    assert memory.get_analysis_state()["status"] == "failed"


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
        str(Path("C:/AI-Studio")),
    ]


@pytest.mark.unit
def test_project_memory_sync_stores_repository_analysis():

    analysis = {
        "generated_at": ("2026-08-20 21:00:00"),
        "overview": {
            "python_files": 10,
            "total_lines": 100,
        },
        "module_roles": {
            "agents/chat_agent.py": ("Conversational agent"),
        },
        "definitions": {
            "agents/chat_agent.py": ["class ChatAgent"],
        },
        "tools": [],
        "registry_names": [],
        "wiring_checks": [],
        "issues": [],
    }

    analyzer = FakeRepositoryAnalyzer(analysis)

    project_memory = FakeProjectMemory()

    sync = ProjectMemorySync(
        repository_analyzer=analyzer,
        project_memory=project_memory,
        workspace="C:/AI-Studio",
    )

    result = sync.sync(["agents/chat_agent.py"])

    assert result == analysis

    assert project_memory.calls == [("repository_analysis", analysis)]
