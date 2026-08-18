from pathlib import Path

import pytest

from tools.atomic_writer import AtomicWriter


@pytest.mark.unit
def test_atomic_writer_writes_content(tmp_path):

    target = tmp_path / "app.py"

    target.write_text(
        "old = True\n",
        encoding="utf-8",
    )

    writer = AtomicWriter(
        workspace=tmp_path
    )

    result = writer.write(
        target,
        "new = True\n"
    )

    assert result["success"] is True

    assert target.read_text(
        encoding="utf-8"
    ) == "new = True\n"


@pytest.mark.unit
def test_atomic_writer_preserves_file_on_failure(tmp_path):

    target = tmp_path / "app.py"

    original = "old = True\n"

    target.write_text(
        original,
        encoding="utf-8",
    )

    writer = AtomicWriter(
        workspace=tmp_path
    )

    result = writer.write(
        target,
        "new = True\n",
        simulate_failure=True,
    )

    assert result["success"] is False

    assert target.read_text(
        encoding="utf-8"
    ) == original


@pytest.mark.unit
def test_atomic_writer_blocks_path_outside_workspace(tmp_path):

    workspace = tmp_path / "workspace"
    workspace.mkdir()

    outside = tmp_path / "outside.py"

    outside.write_text(
        "old = True\n",
        encoding="utf-8",
    )

    writer = AtomicWriter(
        workspace=workspace
    )

    result = writer.write(
        outside,
        "new = True\n"
    )

    assert result["success"] is False

    assert outside.read_text(
        encoding="utf-8"
    ) == "old = True\n"


@pytest.mark.unit
def test_atomic_writer_creates_target_content_exactly(tmp_path):

    target = tmp_path / "app.py"

    writer = AtomicWriter(
        workspace=tmp_path
    )

    content = (
        "class Example:\n"
        "    value = 42\n"
    )

    result = writer.write(
        target,
        content
    )

    assert result["success"] is True

    assert target.read_text(
        encoding="utf-8"
    ) == content