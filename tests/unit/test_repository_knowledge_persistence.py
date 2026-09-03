import os

import pytest

from memory.project_memory.project_memory import ProjectMemory


@pytest.mark.unit
def test_project_memory_initializes_domain_separated_repository_stores(tmp_path):
    memory = ProjectMemory(tmp_path)

    for name in (
        "project.json",
        "files.json",
        "symbols.json",
        "dependencies.json",
        "relationships.json",
        "architecture.json",
        "analysis_state.json",
    ):
        assert (tmp_path / ".ai_memory" / name).exists()

    assert memory.get_analysis_state()["status"] == "uninitialized"


@pytest.mark.unit
def test_project_memory_syncs_general_repository_domains(tmp_path):
    memory = ProjectMemory(tmp_path)
    analysis = {
        "schema_version": 2,
        "generated_at": "2026-08-24 12:00:00",
        "repository_root": str(tmp_path.resolve()),
        "overview": {"total_files": 1},
        "files": {
            "app.ts": {
                "language": "typescript",
                "content_hash": "sha256:test",
            }
        },
        "symbols": {"app.ts": [{"name": "value", "kind": "variable"}]},
        "dependencies": {"app.ts": []},
        "relationships": [{"source": "app.ts", "target": "README.md", "kind": "docs"}],
        "definitions": {},
        "module_roles": {},
    }

    assert memory.sync_repository_analysis(analysis) is True
    assert memory.get_symbols()["app.ts"][0]["name"] == "value"
    assert memory.get_dependencies()["app.ts"] == []
    assert len(memory.get_relationships()["edges"]) == 1
    assert memory.get_analysis_state()["status"] == "ready"
    assert memory.get_analysis_state()["files_indexed"] == 1


@pytest.mark.unit
def test_project_memory_does_not_mark_snapshot_ready_after_store_failure(
    tmp_path,
    monkeypatch,
):
    memory = ProjectMemory(tmp_path)

    memory.project_store.save(
        {"name": "original"}
    )

    memory.files_store.save(
        {"original.py": {"language": "python"}}
    )

    memory.symbols_store.save(
        {"original.py": [{"name": "original"}]}
    )

    original_files = memory.load_json(
        memory.files_file
    )
    original_symbols = memory.load_json(
        memory.symbols_file
    )

    analysis = {
        "schema_version": 2,
        "generated_at": "2026-08-24 12:00:00",
        "repository_root": str(tmp_path.resolve()),
        "generation_id": "generation-2",
        "repository_fingerprint": "sha256:fingerprint-2",
        "overview": {"total_files": 1},
        "files": {
            "app.py": {
                "language": "python"
            }
        },
        "symbols": {},
        "dependencies": {},
        "relationships": [],
        "definitions": {},
        "module_roles": {},
    }

    def fail_replace(source, destination):
        raise OSError("store unavailable")

    monkeypatch.setattr(
        "app.core.storage.json_store.os.replace",
        fail_replace,
    )

    assert memory.sync_repository_analysis(
        analysis
    ) is False

    assert memory.load_json(
        memory.files_file
    ) == original_files

    assert memory.load_json(
        memory.symbols_file
    ) == original_symbols

    assert memory.load_json(
        memory.project_file
    ) == {"name": "original"}

    assert memory.get_analysis_state()[
        "status"
    ] != "ready"

@pytest.mark.unit
def test_project_memory_sync_rolls_back_domain_stores_on_commit_failure(
    tmp_path,
    monkeypatch,
):
    memory = ProjectMemory(tmp_path)

    memory.files_store.save(
        {
            "original.py": {
                "language": "python",
            }
        }
    )

    memory.symbols_store.save(
        {
            "original.py": [
                {
                    "name": "original",
                }
            ]
        }
    )

    memory.dependencies_store.save(
        {
            "original.py": []
        }
    )

    memory.relationships_store.save(
        {
            "edges": [
                {
                    "source": "original.py",
                    "target": "original.py",
                    "kind": "dependency",
                }
            ]
        }
    )

    memory.architecture_store.save(
        {
            "repository_analysis": {
                "old": True,
            }
        }
    )

    memory.project_store.save(
        {
            "name": "original",
        }
    )

    original_files = memory.load_json(
        memory.files_file
    )
    original_symbols = memory.load_json(
        memory.symbols_file
    )
    original_dependencies = memory.load_json(
        memory.dependencies_file
    )
    original_relationships = memory.load_json(
        memory.relationships_file
    )
    original_architecture = memory.load_json(
        memory.architecture_file
    )
    original_project = memory.load_json(
        memory.project_file
    )

    analysis = {
        "schema_version": 2,
        "generated_at": "2026-08-24 12:00:00",
        "repository_root": str(
            tmp_path.resolve()
        ),
        "generation_id": "generation-2",
        "repository_fingerprint": "sha256:fingerprint-2",
        "overview": {
            "total_files": 1,
        },
        "files": {
            "new.py": {
                "language": "python",
            }
        },
        "symbols": {
            "new.py": [
                {
                    "name": "new",
                }
            ]
        },
        "dependencies": {
            "new.py": [],
        },
        "relationships": [],
        "definitions": {},
        "module_roles": {},
    }

    original_replace = os.replace
    replace_count = 0

    def fail_on_fourth_replace(source, destination):
        nonlocal replace_count

        replace_count += 1

        if replace_count == 4:
            raise OSError("commit failed")

        original_replace(
            source,
            destination,
        )

    monkeypatch.setattr(
        "app.core.storage.json_store.os.replace",
        fail_on_fourth_replace,
    )

    assert memory.sync_repository_analysis(
        analysis
    ) is False

    assert memory.load_json(
        memory.files_file
    ) == original_files

    assert memory.load_json(
        memory.symbols_file
    ) == original_symbols

    assert memory.load_json(
        memory.dependencies_file
    ) == original_dependencies

    assert memory.load_json(
        memory.relationships_file
    ) == original_relationships

    assert memory.load_json(
        memory.architecture_file
    ) == original_architecture

    assert memory.load_json(
        memory.project_file
    ) == original_project

    assert memory.get_analysis_state()[
        "status"
    ] == "failed"