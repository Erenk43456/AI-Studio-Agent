import pytest

from tools.tool_registry import ToolRegistry
from tools.validation_tool import ValidationTool


@pytest.fixture
def validator(tmp_path):
    return ValidationTool(
        workspace=tmp_path,
    )


@pytest.mark.unit
def test_validation_tool_metadata(
    validator,
):
    assert validator.name == "validation"
    assert validator.description
    assert validator.purpose
    assert validator.safe is True
    assert validator.modifies_files is False
    assert validator.requires_confirmation is False


@pytest.mark.unit
def test_validation_tool_rejects_non_dict(
    validator,
):
    result = validator.execute(
        "invalid"
    )

    assert result == {
        "success": False,
        "message": "Invalid validation request.",
    }


@pytest.mark.unit
def test_validation_tool_rejects_missing_files(
    validator,
):
    result = validator.execute({})

    assert result == {
        "success": False,
        "message": "No files were provided.",
    }


@pytest.mark.unit
def test_validation_tool_rejects_invalid_files_list(
    validator,
):
    result = validator.execute(
        {
            "files": "parser.py",
        }
    )

    assert result == {
        "success": False,
        "message": "Invalid files list.",
    }


@pytest.mark.unit
def test_validation_tool_validates_python_file(
    validator,
    tmp_path,
):
    source = tmp_path / "parser.py"

    source.write_text(
        """\
class Parser:
    def parse(self, value):
        return value
""",
        encoding="utf-8",
    )

    result = validator.execute(
        {
            "files": [
                "parser.py",
            ],
        }
    )

    assert result["success"] is True
    assert result["valid"] is True
    assert result["results"] == [
        {
            "file": "parser.py",
            "valid": True,
            "error": None,
        }
    ]


@pytest.mark.unit
def test_validation_tool_detects_python_syntax_error(
    validator,
    tmp_path,
):
    source = tmp_path / "parser.py"

    source.write_text(
        """\
class Parser:
    def parse(self, value)
        return value
""",
        encoding="utf-8",
    )

    result = validator.execute(
        {
            "files": [
                "parser.py",
            ],
        }
    )

    assert result["success"] is True
    assert result["valid"] is False
    assert result["results"][0]["file"] == (
        "parser.py"
    )
    assert result["results"][0]["valid"] is False
    assert result["results"][0]["error"]


@pytest.mark.unit
def test_validation_tool_validates_multiple_files(
    validator,
    tmp_path,
):
    valid = tmp_path / "valid.py"
    invalid = tmp_path / "invalid.py"

    valid.write_text(
        """\
def run():
    return True
""",
        encoding="utf-8",
    )

    invalid.write_text(
        """\
def run()
    return True
""",
        encoding="utf-8",
    )

    result = validator.execute(
        {
            "files": [
                "valid.py",
                "invalid.py",
            ],
        }
    )

    assert result["success"] is True
    assert result["valid"] is False
    assert len(result["results"]) == 2

    assert result["results"][0]["file"] == (
        "valid.py"
    )
    assert result["results"][0]["valid"] is True

    assert result["results"][1]["file"] == (
        "invalid.py"
    )
    assert result["results"][1]["valid"] is False


@pytest.mark.unit
def test_validation_tool_returns_file_not_found(
    validator,
):
    result = validator.execute(
        {
            "files": [
                "missing.py",
            ],
        }
    )

    assert result["success"] is True
    assert result["valid"] is False
    assert result["results"] == [
        {
            "file": "missing.py",
            "valid": False,
            "error": "File not found.",
        }
    ]


@pytest.mark.unit
def test_validation_tool_rejects_path_outside_workspace(
    validator,
):
    result = validator.execute(
        {
            "files": [
                "../outside.py",
            ],
        }
    )

    assert result["success"] is True
    assert result["valid"] is False
    assert result["results"][0]["file"] == (
        "../outside.py"
    )
    assert result["results"][0]["valid"] is False
    assert result["results"][0]["error"] == (
        "Path is outside the workspace."
    )


@pytest.mark.unit
def test_validation_tool_rejects_directory(
    validator,
    tmp_path,
):
    directory = tmp_path / "parser.py"
    directory.mkdir()

    result = validator.execute(
        {
            "files": [
                "parser.py",
            ],
        }
    )

    assert result["success"] is True
    assert result["valid"] is False
    assert result["results"] == [
        {
            "file": "parser.py",
            "valid": False,
            "error": "Target is not a file.",
        }
    ]


@pytest.mark.unit
def test_validation_tool_does_not_modify_file(
    validator,
    tmp_path,
):
    source = tmp_path / "parser.py"

    original = """\
class Parser:
    def parse(self, value):
        return value
"""

    source.write_text(
        original,
        encoding="utf-8",
    )

    result = validator.execute(
        {
            "files": [
                "parser.py",
            ],
        }
    )

    assert result["valid"] is True

    assert source.read_text(
        encoding="utf-8"
    ) == original

@pytest.mark.unit
def test_validation_tool_can_be_registered_and_executed(tmp_path):

    registry = ToolRegistry()

    validation = ValidationTool(
        tmp_path
    )

    registry.register(
        "validation",
        validation
    )

    valid_file = (
        tmp_path / "valid.py"
    )

    valid_file.write_text(
        "x = 1\n",
        encoding="utf-8"
    )

    result = registry.execute(
        "validation",
        {
            "files": [
                "valid.py"
            ]
        }
    )

    assert result["success"] is True
    assert result["tool"] == "validation"

    validation_result = result["result"]

    assert validation_result["success"] is True
    assert validation_result["valid"] is True

    assert validation_result["results"] == [
        {
            "file": "valid.py",
            "valid": True,
            "error": None,
        }
    ]