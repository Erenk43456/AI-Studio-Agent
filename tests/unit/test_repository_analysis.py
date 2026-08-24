import json

import pytest

from tools.repository_analysis import RepositoryAnalysis


@pytest.mark.unit
def test_repository_analysis_serializes_general_and_legacy_fields():
    analysis = RepositoryAnalysis(
        generated_at="2026-08-24 12:00:00",
        repository_root="C:/workspace",
        languages={"python": 1, "typescript": 2},
        files={"app.ts": {"language": "typescript"}},
        definitions={"main.py": ["def main("]},
    )

    data = analysis.to_dict()

    assert data["schema_version"] == 2
    assert data["repository_root"] == "C:/workspace"
    assert data["languages"]["typescript"] == 2
    assert data["definitions"]["main.py"] == ["def main("]
    json.dumps(data)


@pytest.mark.unit
def test_repository_analysis_preserves_legacy_positional_field_order():
    analysis = RepositoryAnalysis(
        "timestamp",
        {"root": "workspace"},
        {"module.py": "module"},
        {"module.py": ["def run("]},
    )

    assert analysis.generated_at == "timestamp"
    assert analysis.overview == {"root": "workspace"}
    assert analysis.module_roles == {"module.py": "module"}
    assert analysis.definitions == {"module.py": ["def run("]}
