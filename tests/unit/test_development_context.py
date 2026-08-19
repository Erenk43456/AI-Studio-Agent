import json

import pytest

from app.core.development_context import DevelopmentContext


class FakeProjectMemory:

    def __init__(self, files=None, architecture=None):
        self.files = files or {}
        self.architecture = architecture or {}
        self.get_file_calls = []

    def get_all_files(self):
        return self.files

    def get_file(self, path):
        self.get_file_calls.append(path)
        return self.files.get(path)

    def get_architecture(self):
        return self.architecture


class FailingProjectMemory:

    def get_all_files(self):
        raise RuntimeError("memory unavailable")

    def get_architecture(self):
        raise RuntimeError("architecture unavailable")

    def get_file(self, path):
        raise RuntimeError("file unavailable")


@pytest.fixture
def context():
    return DevelopmentContext(
        FakeProjectMemory(),
        "C:/AI-Studio",
    )


@pytest.mark.unit
def test_extract_target_files_normalizes_and_deduplicates(context):

    result = context.extract_target_files(
        "Fix ./app\\core\\parser.py "
        "and app/core/parser.py; "
        "inspect tools/helper.py."
    )

    assert result == [
        "app/core/parser.py",
        "tools/helper.py",
    ]


@pytest.mark.unit
def test_build_collects_targets_related_files_relationships_and_strategy():

    files = {
        "app/core/parser.py": {
            "imports": [
                "app/core/tokenizer.py"
            ],
            "summary": "Parser implementation",
        },

        "app/core/tokenizer.py": {
            "imports": [],
            "summary": "Tokenizer used by parser",
        },

        "tools/unrelated.py": {
            "summary": "Unrelated utility",
        },
    }

    architecture = {
        "components": [
            "app/core/parser.py",
            "app/core/tokenizer.py",
        ],
    }

    memory = FakeProjectMemory(
        files=files,
        architecture=architecture,
    )

    context = DevelopmentContext(
        memory,
        "C:/AI-Studio",
    )

    result = context.build(
        "Fix the bug in app/core/parser.py"
    )

    assert result["task"] == (
        "Fix the bug in app/core/parser.py"
    )

    assert result["targets"] == [
        "app/core/parser.py"
    ]

    assert result["target_files"] == {
        "app/core/parser.py": files[
            "app/core/parser.py"
        ]
    }

    assert "app/core/tokenizer.py" in result[
        "related_files"
    ]

    assert "app/core/parser.py" not in result[
        "related_files"
    ]

    assert result["relationships"][
        "app/core/parser.py"
    ]

    assert result["strategy"]["type"] == (
        "architecture_aware_targeted_fix"
    )

    assert result["strategy"]["memory_first"] is True
    assert result["strategy"]["architecture_aware"] is True
    assert result["strategy"]["minimal_change"] is True


@pytest.mark.unit
def test_find_related_files_scores_same_package_and_dependency_relationships():

    files = {
        "app/core/parser.py": {
            "imports": [
                "app/core/tokenizer.py"
            ],
        },

        "app/core/tokenizer.py": {
            "imports": [
                "app/core/parser.py"
            ],
        },

        "app/tools.py": {
            "imports": [],
        },
    }

    context = DevelopmentContext(
        FakeProjectMemory(files=files),
        "C:/AI-Studio",
    )

    related = context.find_related_files(
        "fix parser",
        ["app/core/parser.py"],
        files,
        {},
    )

    tokenizer = related[
        "app/core/tokenizer.py"
    ]

    assert tokenizer["score"] > 5

    assert "same_package" in tokenizer[
        "relationships"
    ]

    assert "references_target" in tokenizer[
        "relationships"
    ]

    assert "app/tools.py" not in related


@pytest.mark.unit
def test_architecture_relationship_adds_architecture_score(context):

    score, reasons, relationships = (
        context.score_architecture_relationship(
            "app/core/tokenizer.py",
            ["app/core/parser.py"],
            {
                "files": [
                    "app/core/parser.py",
                    "app/core/tokenizer.py",
                ]
            },
            {},
        )
    )

    assert score >= 9

    assert (
        "both files appear in project architecture"
        in reasons
    )

    assert "architecture_member" in relationships
    assert "architecture_layer" in relationships


@pytest.mark.unit
def test_determine_strategy_selects_expected_strategy_types():

    context = DevelopmentContext(
        FakeProjectMemory(),
        "C:/AI-Studio",
    )

    cases = [
        (
            "Analyze app/core/parser.py",
            "analysis",
        ),

        (
            "Refactor app/core/parser.py",
            "architecture_preserving_refactor",
        ),

        (
            "Fix app/core/parser.py",
            "targeted_fix",
        ),

        (
            "Add a feature to app/core/parser.py",
            "feature_implementation",
        ),

        (
            "Work on app/core/parser.py",
            "architecture_aware_development",
        ),
    ]

    for task, expected in cases:

        result = context.build(
            task
        )

        assert result["strategy"]["type"] == (
            expected
        )


@pytest.mark.unit
def test_multiple_targets_use_multi_target_fix_strategy():

    files = {
        "app/core/parser.py": {},
        "app/core/tokenizer.py": {},
    }

    context = DevelopmentContext(
        FakeProjectMemory(files=files),
        "C:/AI-Studio",
    )

    result = context.build(
        "Fix app/core/parser.py "
        "and app/core/tokenizer.py"
    )

    assert result["targets"] == [
        "app/core/parser.py",
        "app/core/tokenizer.py",
    ]

    assert result["strategy"]["multi_target"] is True

    assert result["strategy"]["type"] == (
        "multi_target_targeted_fix"
    )


@pytest.mark.unit
def test_repository_analysis_fallback_is_enabled_when_memory_is_empty():

    context = DevelopmentContext(
        FakeProjectMemory(),
        "C:/AI-Studio",
    )

    result = context.build(
        "Fix app/core/parser.py"
    )

    assert result["strategy"]["memory_available"] is False

    assert result["strategy"][
        "repository_analysis_fallback"
    ] is True


@pytest.mark.unit
def test_memory_errors_fall_back_to_empty_context():

    context = DevelopmentContext(
        FailingProjectMemory(),
        "C:/AI-Studio",
    )

    result = context.build(
        "Fix app/core/parser.py"
    )

    assert result["target_files"] == {}
    assert result["related_files"] == {}
    assert result["architecture"] == {}

    assert result["strategy"]["memory_available"] is False

    assert result["strategy"][
        "repository_analysis_fallback"
    ] is True


@pytest.mark.unit
def test_to_prompt_returns_valid_json():

    context = DevelopmentContext(
        FakeProjectMemory(),
        "C:/AI-Studio",
    )

    value = {
        "task": "Fix parser",
        "strategy": {
            "type": "targeted_fix",
        },
    }

    prompt = context.to_prompt(
        value
    )

    parsed = json.loads(
        prompt
    )

    assert parsed == value


# =============================================================
# Relationship filtering
# =============================================================


@pytest.mark.unit
def test_same_layer_or_directory_alone_does_not_make_file_related():

    files = {
        "app/core/parser.py": {
            "summary": "Parser implementation",
        },

        "app/core/unrelated.py": {
            "summary": "Completely unrelated module",
        },

        "app/tools.py": {
            "summary": "Unrelated tool",
        },
    }

    context = DevelopmentContext(
        FakeProjectMemory(files=files),
        "C:/AI-Studio",
    )

    related = context.find_related_files(
        "Fix app/core/parser.py",
        ["app/core/parser.py"],
        files,
        {
            "layers": {
                "core": [
                    "app/core/parser.py",
                    "app/core/unrelated.py",
                ],

                "tools": [
                    "app/tools.py"
                ],
            }
        },
    )

    assert related == {}


@pytest.mark.unit
def test_direct_dependency_reference_is_meaningful_relationship():

    context = DevelopmentContext(
        FakeProjectMemory(),
        "C:/AI-Studio",
    )

    score, reasons, relationships = (
        context.score_dependency_relationship(
            "app/core/tokenizer.py",
            ["app/core/parser.py"],
            {
                "imports": [
                    "app/core/parser.py"
                ],

                "summary": (
                    "Tokenizer depends on parser"
                ),
            },
        )
    )

    assert score >= 7

    assert any(
        "references target" in reason
        for reason in reasons
    )

    assert "references_target" in relationships


@pytest.mark.unit
def test_target_memory_reference_makes_related_file_meaningful():

    files = {
        "app/core/parser.py": {
            "imports": [
                "app/core/tokenizer.py"
            ],
        },

        "app/core/tokenizer.py": {
            "summary": "Tokenizer",
        },
    }

    context = DevelopmentContext(
        FakeProjectMemory(files=files),
        "C:/AI-Studio",
    )

    related = context.find_related_files(
        "Fix parser",
        ["app/core/parser.py"],
        files,
        {},
    )

    tokenizer = related[
        "app/core/tokenizer.py"
    ]

    assert "target_references_file" in tokenizer[
        "relationships"
    ]

    assert tokenizer["score"] >= 5


@pytest.mark.unit
def test_architecture_layer_is_supporting_evidence_not_meaningful_relationship():

    context = DevelopmentContext(
        FakeProjectMemory(),
        "C:/AI-Studio",
    )

    score, reasons, relationships = (
        context.score_architecture_relationship(
            "app/core/unrelated.py",
            ["app/core/parser.py"],
            {
                "layers": {
                    "core": [
                        "app/core/parser.py"
                    ]
                }
            },
            {},
        )
    )

    assert score == 1

    assert "architecture_layer" in relationships

    assert "architecture_member" not in relationships

    assert "architecture_reference" not in relationships


# =============================================================
# Architecture-aware feature implementation
# =============================================================


@pytest.mark.unit
def test_feature_with_architecture_related_file_uses_architecture_aware_strategy():

    files = {
        "app/core/parser.py": {
            "summary": "Parser implementation",
        },

        "app/core/tokenizer.py": {
            "summary": "Tokenizer integration",
        },
    }

    architecture = {
        "components": [
            {
                "name": "parser",
                "files": [
                    "app/core/parser.py",
                ],
                "dependencies": [
                    "app/core/tokenizer.py",
                ],
            },
            {
                "name": "tokenizer",
                "files": [
                    "app/core/tokenizer.py",
                ],
            },
        ],
    }

    class ArchitectureProjectMemory(FakeProjectMemory):

        def get_architecture(self):
            return architecture

    context = DevelopmentContext(
        ArchitectureProjectMemory(
            files=files
        ),
        "C:/AI-Studio",
    )

    result = context.build(
        "Add a feature to app/core/parser.py"
    )

    assert result["strategy"]["type"] == (
        "architecture_aware_feature_implementation"
    )

    assert "app/core/tokenizer.py" in (
        result["related_files"]
    )

    assert (
        "architecture_member"
        in result["related_files"][
            "app/core/tokenizer.py"
        ]["relationships"]
    )