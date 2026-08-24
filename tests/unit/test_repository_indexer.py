import json

import pytest

from tools.repository_indexer import RepositoryIndexer


@pytest.mark.unit
def test_repository_indexer_collects_mixed_language_metadata(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("print('x')\n", encoding="utf-8")
    (tmp_path / "src" / "app.ts").write_text("export const x = 1;\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("docs\n", encoding="utf-8")
    (tmp_path / "package.json").write_text("{}", encoding="utf-8")

    result = RepositoryIndexer().index(tmp_path)

    assert result["total_files"] == 4
    assert result["languages"]["python"] == 1
    assert result["languages"]["typescript"] == 1
    assert result["configuration_files"] == ["package.json"]
    assert result["documentation_files"] == ["README.md"]
    assert result["files"]["src/app.py"]["content_hash"].startswith("sha256:")


@pytest.mark.unit
def test_repository_indexer_skips_ai_memory_and_is_json_serializable(tmp_path):
    (tmp_path / ".ai_memory").mkdir()
    (tmp_path / ".ai_memory" / "files.json").write_text("{}", encoding="utf-8")
    (tmp_path / "main.js").write_text("console.log('x')", encoding="utf-8")

    result = RepositoryIndexer().index(tmp_path)

    assert "main.js" in result["files"]
    assert ".ai_memory/files.json" not in result["files"]
    json.dumps(result)
