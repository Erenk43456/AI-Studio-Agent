import pytest

from tools.file_tool import FileTool


@pytest.fixture
def file_tool(tmp_path):
    return FileTool(
        workspace=tmp_path
    )


@pytest.mark.unit
def test_file_tool_metadata(file_tool):
    assert file_tool.name == "file"
    assert file_tool.description
    assert file_tool.purpose
    assert file_tool.safe is False
    assert file_tool.modifies_files is True
    assert file_tool.requires_confirmation is True
    assert file_tool.version == "1.0"


@pytest.mark.unit
def test_file_tool_uses_workspace_as_base_path(tmp_path):
    tool = FileTool(
        workspace=tmp_path
    )

    assert tool.base_path == tmp_path.resolve()


@pytest.mark.unit
def test_file_tool_execute_rejects_non_dict(file_tool):
    result = file_tool.execute(
        "invalid request"
    )

    assert result == {
        "success": False,
        "error": "Invalid file request.",
    }


@pytest.mark.unit
def test_file_tool_execute_defaults_to_read(file_tool):
    result = file_tool.execute(
        {
            "filename": "missing.txt",
        }
    )

    assert result == {
        "success": False,
        "error": "File not found: missing.txt",
    }


@pytest.mark.unit
def test_file_tool_rejects_unknown_action(file_tool):
    result = file_tool.execute(
        {
            "action": "delete",
            "filename": "test.txt",
        }
    )

    assert result == {
        "success": False,
        "error": "Unknown action: delete",
    }


@pytest.mark.unit
def test_file_tool_create_file(file_tool, tmp_path):
    result = file_tool.execute(
        {
            "action": "create",
            "filename": "test.txt",
            "content": "Hello AI-Studio",
        }
    )

    assert result["success"] is True
    assert result["action"] == "create"
    assert result["file"] == str(
        tmp_path / "test.txt"
    )
    assert result["message"] == "File created."

    assert (
        tmp_path / "test.txt"
    ).read_text(
        encoding="utf-8"
    ) == "Hello AI-Studio"


@pytest.mark.unit
def test_file_tool_create_file_with_nested_directory(
    file_tool,
    tmp_path,
):
    result = file_tool.create_file(
        "src/parser/test.txt",
        "parser test",
    )

    assert result["success"] is True

    path = (
        tmp_path
        / "src"
        / "parser"
        / "test.txt"
    )

    assert path.exists()
    assert path.read_text(
        encoding="utf-8"
    ) == "parser test"


@pytest.mark.unit
def test_file_tool_create_file_missing_filename(file_tool):
    result = file_tool.create_file(
        None,
        "content",
    )

    assert result == {
        "success": False,
        "error": "Filename missing.",
    }


@pytest.mark.unit
def test_file_tool_read_file(file_tool, tmp_path):
    path = tmp_path / "test.txt"

    path.write_text(
        "Hello World",
        encoding="utf-8",
    )

    result = file_tool.execute(
        {
            "action": "read",
            "filename": "test.txt",
        }
    )

    assert result == {
        "success": True,
        "action": "read",
        "file": str(path),
        "content": "Hello World",
    }


@pytest.mark.unit
def test_file_tool_read_missing_file(file_tool):
    result = file_tool.read_file(
        "missing.txt"
    )

    assert result == {
        "success": False,
        "error": "File not found: missing.txt",
    }


@pytest.mark.unit
def test_file_tool_write_existing_file_creates_backup(
    file_tool,
    tmp_path,
):
    path = tmp_path / "test.txt"

    path.write_text(
        "old content",
        encoding="utf-8",
    )

    result = file_tool.write_file(
        "test.txt",
        "new content",
    )

    assert result["success"] is True
    assert result["action"] == "write"
    assert result["file"] == str(path)
    assert result["message"] == "File updated."

    assert path.read_text(
        encoding="utf-8"
    ) == "new content"

    backup = result["backup"]

    assert backup is not None

    backup_path = tmp_path / (
        path.name
        + backup.split(
            path.name
        )[-1]
    )

    assert backup_path.exists()
    assert backup_path.read_text(
        encoding="utf-8"
    ) == "old content"


@pytest.mark.unit
def test_file_tool_blocks_incomplete_generated_content(
    file_tool,
):
    result = file_tool.write_file(
        "test.txt",
        "def foo():\n"
        "    <existing content>\n",
    )

    assert result == {
        "success": False,
        "error": (
            "Incomplete generated content."
        ),
    }

@pytest.mark.unit
def test_file_tool_rejects_path_outside_workspace(
    file_tool,
    tmp_path,
):
    outside_file = tmp_path.parent / "outside.txt"

    with pytest.raises(
        PermissionError,
        match="Access outside workspace denied.",
    ):
        file_tool.get_path(
            "../outside.txt"
        )


@pytest.mark.unit
def test_file_tool_rejects_absolute_path_outside_workspace(
    file_tool,
    tmp_path,
):
    outside_file = (
        tmp_path.parent
        / "outside.txt"
    )

    with pytest.raises(
        PermissionError,
        match="Access outside workspace denied.",
    ):
        file_tool.get_path(
            str(outside_file)
        )


@pytest.mark.unit
def test_file_tool_get_path_returns_none_for_missing_filename(
    file_tool,
):
    assert file_tool.get_path(None) is None
    assert file_tool.get_path("") is None


@pytest.mark.unit
def test_file_tool_get_path_returns_resolved_workspace_path(
    file_tool,
    tmp_path,
):
    result = file_tool.get_path(
        "src/parser.py"
    )

    assert result == (
        tmp_path
        / "src"
        / "parser.py"
    ).resolve()


@pytest.mark.unit
def test_file_tool_write_missing_filename(file_tool):
    result = file_tool.write_file(
        None,
        "content",
    )

    assert result == {
        "success": False,
        "error": "Filename missing.",
    }


@pytest.mark.unit
def test_file_tool_write_blocks_none_content(file_tool):
    result = file_tool.write_file(
        "test.txt",
        None,
    )

    assert result == {
        "success": False,
        "error": "Empty content blocked.",
    }


@pytest.mark.unit
def test_file_tool_write_allows_empty_string_content(
    file_tool,
    tmp_path,
):
    result = file_tool.write_file(
        "empty.txt",
        "",
    )

    assert result["success"] is True

    path = tmp_path / "empty.txt"

    assert path.exists()
    assert path.read_text(
        encoding="utf-8"
    ) == ""


@pytest.mark.unit
def test_file_tool_create_defaults_to_empty_content(
    file_tool,
    tmp_path,
):
    result = file_tool.create_file(
        "empty.txt"
    )

    assert result["success"] is True

    path = tmp_path / "empty.txt"

    assert path.exists()
    assert path.read_text(
        encoding="utf-8"
    ) == ""


@pytest.mark.unit
def test_file_tool_create_replaces_existing_file(
    file_tool,
    tmp_path,
):
    path = tmp_path / "test.txt"

    path.write_text(
        "old",
        encoding="utf-8",
    )

    result = file_tool.create_file(
        "test.txt",
        "new",
    )

    assert result["success"] is True
    assert path.read_text(
        encoding="utf-8"
    ) == "new"


@pytest.mark.unit
def test_file_tool_write_blocks_existing_content_placeholder(
    file_tool,
    tmp_path,
):
    path = tmp_path / "test.txt"

    path.write_text(
        "original",
        encoding="utf-8",
    )

    result = file_tool.write_file(
        "test.txt",
        "new\n<existing content>\n",
    )

    assert result == {
        "success": False,
        "error": (
            "Incomplete generated content."
        ),
    }

    assert path.read_text(
        encoding="utf-8"
    ) == "original"


@pytest.mark.unit
def test_file_tool_atomic_write_creates_parent_directory(
    file_tool,
    tmp_path,
):
    path = (
        tmp_path
        / "nested"
        / "directory"
        / "file.txt"
    )

    file_tool.atomic_write(
        path,
        "atomic content",
    )

    assert path.exists()
    assert path.read_text(
        encoding="utf-8"
    ) == "atomic content"


@pytest.mark.unit
def test_file_tool_read_rejects_workspace_escape(
    file_tool,
):
    result = file_tool.read_file(
        "../outside.txt"
    )

    assert result["success"] is False
    assert (
        result["error"]
        == "Access outside workspace denied."
    )


@pytest.mark.unit
def test_file_tool_write_rejects_workspace_escape(
    file_tool,
):
    result = file_tool.write_file(
        "../outside.txt",
        "malicious content",
    )

    assert result["success"] is False
    assert (
        result["error"]
        == "Access outside workspace denied."
    )


@pytest.mark.unit
def test_file_tool_create_rejects_workspace_escape(
    file_tool,
):
    result = file_tool.create_file(
        "../outside.txt",
        "malicious content",
    )

    assert result["success"] is False
    assert (
        result["error"]
        == "Access outside workspace denied."
    )