import pytest

from app.core.repository_context_resolver import RepositoryContextResolver


class SnapshotMemory:
    def __init__(self):
        self.files = {
            "app/a.py": {"language": "python"},
            "app/b.py": {"language": "python"},
            "tests/test_a.py": {"category": "test"},
            "app/c.py": {"language": "python"},
        }
        self.symbols = {
            "app/a.py": [{"id": "app/a.py::A", "name": "A", "line": 2}],
        }
        self.dependencies = {
            "app/a.py": [
                {"source": "app/a.py", "target": "app/b.py", "kind": "import"}
            ],
        }
        self.relationships = {
            "edges": [
                {"source": "app/b.py", "target": "app/a.py", "kind": "calls"},
                {"source": "tests/test_a.py", "target": "app/a.py", "kind": "tests"},
                {"source": "app/a.py", "target": "app/c.py", "kind": "uses"},
            ]
        }
        self.calls = []

    def get_all_files(self):
        self.calls.append("files")
        return self.files

    def get_symbols(self):
        self.calls.append("symbols")
        return self.symbols

    def get_dependencies(self):
        self.calls.append("dependencies")
        return self.dependencies

    def get_relationships(self):
        self.calls.append("relationships")
        return self.relationships


@pytest.mark.unit
def test_resolver_returns_target_metadata_symbols_and_dependencies():
    memory = SnapshotMemory()

    result = RepositoryContextResolver(memory).resolve([".\\app\\a.py"], ["A"])

    assert result["targets"] == ["app/a.py"]
    assert result["target_files"]["app/a.py"]["language"] == "python"
    assert result["symbols"]["app/a.py"][0]["name"] == "A"
    assert result["dependencies"]["app/a.py"][0]["target"] == "app/b.py"


@pytest.mark.unit
def test_resolver_includes_direct_and_reverse_relationships():
    result = RepositoryContextResolver(SnapshotMemory()).resolve(["app/a.py"])

    related = {item["file"] for item in result["related_files"]}

    assert related == {"app/b.py", "app/c.py", "tests/test_a.py"}
    assert {item["kind"] for item in result["relationships"]} == {
        "calls",
        "tests",
        "uses",
    }


@pytest.mark.unit
def test_resolver_deduplicates_and_applies_max_files_without_dropping_targets():
    result = RepositoryContextResolver(SnapshotMemory()).resolve(
        ["app/a.py", "app/a.py", "app/b.py"],
        max_files=1,
    )

    assert result["targets"] == ["app/a.py", "app/b.py"]
    assert result["metadata"]["selected_files"] >= 2
    assert len({item["file"] for item in result["related_files"]}) == len(
        result["related_files"]
    )


@pytest.mark.unit
def test_resolver_order_is_deterministic_and_reports_missing_targets():
    resolver = RepositoryContextResolver(SnapshotMemory())

    first = resolver.resolve(["missing.py", "app/a.py"], max_files=3)
    second = resolver.resolve(["missing.py", "app/a.py"], max_files=3)

    assert first == second
    assert first["targets"] == ["missing.py", "app/a.py"]
    assert first["target_files"] == {"app/a.py": {"language": "python"}}


@pytest.mark.unit
def test_resolver_handles_empty_memory_and_missing_relationships():
    class EmptyMemory:
        def get_all_files(self):
            return {}

        def get_symbols(self):
            return {}

        def get_dependencies(self):
            return {}

        def get_relationships(self):
            return {"edges": []}

    result = RepositoryContextResolver(EmptyMemory()).resolve(["missing.py"])

    assert result["targets"] == ["missing.py"]
    assert result["related_files"] == []
    assert result["relationships"] == []
    assert result["metadata"]["truncated"] is False


@pytest.mark.unit
def test_resolver_only_reads_snapshot_api():
    memory = SnapshotMemory()
    resolver = RepositoryContextResolver(memory)

    resolver.resolve(["app/a.py"])

    assert memory.calls == ["files", "symbols", "dependencies", "relationships"]


@pytest.mark.unit
def test_resolver_exposes_relationship_reason_and_score_metadata():
    result = RepositoryContextResolver(SnapshotMemory()).resolve(["app/a.py"])

    item = next(item for item in result["related_files"] if item["file"] == "app/c.py")

    assert item["relationship"] == "outgoing:uses"
    assert item["reason"] == "outgoing uses"
    assert item["score"] > 0


@pytest.mark.unit
def test_resolver_filters_requested_symbols_without_affecting_files():
    memory = SnapshotMemory()
    memory.symbols["app/a.py"].append(
        {"id": "app/a.py::Other", "name": "Other", "line": 1}
    )

    result = RepositoryContextResolver(memory).resolve(
        ["app/a.py"],
        target_symbols=["Missing"],
    )

    assert result["targets"] == ["app/a.py"]
    assert result["symbols"] == {}


@pytest.mark.unit
def test_resolver_marks_truncation_when_related_candidates_exceed_limit():
    result = RepositoryContextResolver(SnapshotMemory()).resolve(
        ["app/a.py"],
        max_files=2,
    )

    assert result["metadata"] == {
        "total_candidates": 3,
        "selected_files": 2,
        "truncated": True,
    }
    assert result["related_files"][0]["file"] == "app/b.py"


@pytest.mark.unit
def test_resolver_keeps_all_targets_even_when_limit_is_zero():
    result = RepositoryContextResolver(SnapshotMemory()).resolve(
        ["app/a.py", "app/b.py"],
        max_files=0,
    )

    assert result["targets"] == ["app/a.py", "app/b.py"]
    assert result["metadata"]["selected_files"] == 2


@pytest.mark.unit
def test_resolver_handles_missing_symbol_and_relationship_safely():
    result = RepositoryContextResolver(SnapshotMemory()).resolve(
        ["app/a.py"],
        target_symbols=["NotPresent"],
    )

    assert result["symbols"] == {}
    assert result["relationships"]


@pytest.mark.unit
def test_resolver_accepts_single_target_path():
    result = RepositoryContextResolver(SnapshotMemory()).resolve("app/a.py")

    assert result["targets"] == ["app/a.py"]


@pytest.mark.unit
def test_resolver_does_not_need_filesystem_or_repository_analyzer():
    class SnapshotOnlyMemory:
        def get_all_files(self):
            return {"app/a.py": {"language": "python"}}

        def get_symbols(self):
            return {}

        def get_dependencies(self):
            return {}

        def get_relationships(self):
            return []

        def analyze(self, root):
            raise AssertionError("RepositoryAnalyzer must not be called")

    result = RepositoryContextResolver(SnapshotOnlyMemory()).resolve(["app/a.py"])

    assert result["target_files"] == {"app/a.py": {"language": "python"}}


@pytest.mark.unit
def test_resolver_normalizes_duplicate_related_paths():
    memory = SnapshotMemory()
    memory.relationships["edges"].extend(
        [
            {"source": ".\\app\\a.py", "target": ".\\app\\b.py", "kind": "uses"},
        ]
    )

    result = RepositoryContextResolver(memory).resolve(["app/a.py"])
    related_paths = [item["file"] for item in result["related_files"]]

    assert related_paths.count("app/b.py") == 1
