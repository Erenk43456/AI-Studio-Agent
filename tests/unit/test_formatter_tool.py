import pytest

from tools.formatter_tool import FormatterTool


@pytest.mark.unit
def test_formatter_format_code_formats_valid_python():
    formatter = FormatterTool()

    result = formatter.format_code(
        "def hello():\n    return 42"
    )

    assert result == {
        "success": True,
        "code": (
            "def hello():\n"
            "    return 42"
        ),
    }


@pytest.mark.unit
def test_formatter_format_code_accepts_code_mapping():
    formatter = FormatterTool()

    result = formatter.format_code(
        {
            "code": (
                "def hello():\n"
                "    return 42"
            )
        }
    )

    assert result == {
        "success": True,
        "code": (
            "def hello():\n"
            "    return 42"
        ),
    }


@pytest.mark.unit
def test_formatter_format_code_accepts_input_mapping():
    formatter = FormatterTool()

    result = formatter.format_code(
        {
            "input": (
                "def hello():\n"
                "    return 42"
            )
        }
    )

    assert result == {
        "success": True,
        "code": (
            "def hello():\n"
            "    return 42"
        ),
    }


@pytest.mark.unit
def test_formatter_format_code_accepts_context_mapping():
    formatter = FormatterTool()

    result = formatter.format_code(
        {
            "context": (
                "def hello():\n"
                "    return 42"
            )
        }
    )

    assert result == {
        "success": True,
        "code": (
            "def hello():\n"
            "    return 42"
        ),
    }


@pytest.mark.unit
def test_formatter_format_code_rejects_empty_code():
    formatter = FormatterTool()

    result = formatter.format_code("   ")

    assert result == {
        "success": False,
        "message": "Code is empty.",
    }


@pytest.mark.unit
def test_formatter_format_code_rejects_invalid_python():
    formatter = FormatterTool()

    result = formatter.format_code(
        "def broken(:\n    pass"
    )

    assert result["success"] is False
    assert result["message"].startswith(
        "Syntax error:"
    )


@pytest.mark.unit
def test_formatter_format_code_rejects_unsupported_input_type():
    formatter = FormatterTool()

    result = formatter.format_code(123)

    assert result == {
        "success": False,
        "message": "Code is empty.",
    }


@pytest.mark.unit
def test_formatter_format_file_formats_python_file_without_writing(
    tmp_path,
):
    source = tmp_path / "parser.py"

    original = (
        "def parser():\n"
        "    return 42\n"
    )

    source.write_text(
        original,
        encoding="utf-8",
    )

    formatter = FormatterTool(
        workspace=tmp_path,
    )

    result = formatter.format_file(
        source,
        write=False,
    )

    assert result == {
        "success": True,
        "code": (
            "def parser():\n"
            "    return 42"
        ),
    }

    assert source.read_text(
        encoding="utf-8"
    ) == original


@pytest.mark.unit
def test_formatter_format_file_writes_formatted_code(
    tmp_path,
):
    source = tmp_path / "parser.py"

    source.write_text(
        "def parser():\n"
        "    return 42\n",
        encoding="utf-8",
    )

    formatter = FormatterTool(
        workspace=tmp_path,
    )

    result = formatter.format_file(
        source,
        write=True,
    )

    assert result == {
        "success": True,
        "code": (
            "def parser():\n"
            "    return 42"
        ),
    }

    assert source.read_text(
        encoding="utf-8"
    ) == (
        "def parser():\n"
        "    return 42\n"
    )


@pytest.mark.unit
def test_formatter_format_file_returns_not_found_for_missing_file(
    tmp_path,
):
    formatter = FormatterTool(
        workspace=tmp_path,
    )

    result = formatter.format_file(
        tmp_path / "missing.py"
    )

    assert result == {
        "success": False,
        "message": "File not found.",
    }


@pytest.mark.unit
def test_formatter_format_file_rejects_non_python_file(
    tmp_path,
):
    source = tmp_path / "notes.txt"

    source.write_text(
        "hello",
        encoding="utf-8",
    )

    formatter = FormatterTool(
        workspace=tmp_path,
    )

    result = formatter.format_file(
        source
    )

    assert result == {
        "success": False,
        "message": (
            "Only Python files are supported."
        ),
    }


@pytest.mark.unit
def test_formatter_execute_formats_plain_code():
    formatter = FormatterTool()

    result = formatter.execute(
        "def hello():\n    return 42"
    )

    assert result == (
        "def hello():\n"
        "    return 42"
    )


@pytest.mark.unit
def test_formatter_execute_returns_error_message_for_invalid_code():
    formatter = FormatterTool()

    result = formatter.execute(
        "def broken(:\n    pass"
    )

    assert result.startswith(
        "Syntax error:"
    )


@pytest.mark.unit
def test_formatter_execute_formats_file_inside_workspace(
    tmp_path,
):
    source = tmp_path / "parser.py"

    source.write_text(
        "def parser():\n"
        "    return 42\n",
        encoding="utf-8",
    )

    formatter = FormatterTool(
        workspace=tmp_path,
    )

    result = formatter.execute(
        {
            "filename": "parser.py",
        }
    )

    assert result == str(
        {
            "success": True,
            "code": (
                "def parser():\n"
                "    return 42"
            ),
        }
    )

    assert source.read_text(
        encoding="utf-8"
    ) == (
        "def parser():\n"
        "    return 42\n"
    )


@pytest.mark.unit
def test_formatter_execute_denies_path_outside_workspace(
    tmp_path,
):
    outside = tmp_path.parent / "outside.py"

    formatter = FormatterTool(
        workspace=tmp_path,
    )

    result = formatter.execute(
        {
            "filename": (
                "../"
                + outside.name
            )
        }
    )

    assert result == str(
        {
            "success": False,
            "message": (
                "Access outside workspace denied."
            ),
        }
    )


@pytest.mark.unit
def test_formatter_execute_without_filename_uses_code():
    formatter = FormatterTool()

    result = formatter.execute(
        {
            "code": (
                "def hello():\n"
                "    return 42"
            )
        }
    )

    assert result == (
        "def hello():\n"
        "    return 42"
    )