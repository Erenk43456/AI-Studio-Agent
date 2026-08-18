from pathlib import Path

import pytest

from app.core.workspace.watcher import WorkspaceWatcher


@pytest.mark.unit
def test_scan_collects_python_files(tmp_path):
    source = tmp_path / "app.py"
    source.write_text(
        "print('hello')",
        encoding="utf-8",
    )

    watcher = WorkspaceWatcher(
        workspace=tmp_path,
        callback=lambda files: None,
    )

    result = watcher.scan()

    assert str(source) in result


@pytest.mark.unit
def test_scan_ignores_skipped_directories(tmp_path):
    normal = tmp_path / "app.py"
    ignored = (
        tmp_path
        / ".ai_memory"
        / "project.py"
    )

    ignored.parent.mkdir()

    normal.write_text(
        "print('hello')",
        encoding="utf-8",
    )

    ignored.write_text(
        "print('ignored')",
        encoding="utf-8",
    )

    watcher = WorkspaceWatcher(
        workspace=tmp_path,
        callback=lambda files: None,
    )

    result = watcher.scan()

    assert str(normal) in result
    assert str(ignored) not in result


@pytest.mark.unit
def test_detect_changes_finds_new_file(tmp_path):
    watcher = WorkspaceWatcher(
        workspace=tmp_path,
        callback=lambda files: None,
    )

    old = {}

    current = {
        "app.py": 1.0,
    }

    assert watcher.detect_changes(current) == [
        "app.py",
    ]


@pytest.mark.unit
def test_detect_changes_finds_modified_file(tmp_path):
    watcher = WorkspaceWatcher(
        workspace=tmp_path,
        callback=lambda files: None,
    )

    watcher.files = {
        "app.py": 1.0,
    }

    current = {
        "app.py": 2.0,
    }

    assert watcher.detect_changes(current) == [
        "app.py",
    ]


@pytest.mark.unit
def test_detect_changes_finds_deleted_file(tmp_path):
    watcher = WorkspaceWatcher(
        workspace=tmp_path,
        callback=lambda files: None,
    )

    watcher.files = {
        "app.py": 1.0,
    }

    current = {}

    assert watcher.detect_changes(current) == [
        "app.py",
    ]


@pytest.mark.unit
def test_detect_changes_returns_empty_when_unchanged(tmp_path):
    watcher = WorkspaceWatcher(
        workspace=tmp_path,
        callback=lambda files: None,
    )

    watcher.files = {
        "app.py": 1.0,
    }

    current = {
        "app.py": 1.0,
    }

    assert watcher.detect_changes(current) == []


@pytest.mark.unit
def test_scan_ignores_non_python_files(tmp_path):
    python_file = tmp_path / "app.py"
    text_file = tmp_path / "notes.txt"

    python_file.write_text(
        "print('hello')",
        encoding="utf-8",
    )

    text_file.write_text(
        "hello",
        encoding="utf-8",
    )

    watcher = WorkspaceWatcher(
        workspace=tmp_path,
        callback=lambda files: None,
    )

    result = watcher.scan()

    assert str(python_file) in result
    assert str(text_file) not in result


@pytest.mark.unit
def test_detect_changes_reports_multiple_changes(tmp_path):
    watcher = WorkspaceWatcher(
        workspace=tmp_path,
        callback=lambda files: None,
    )

    watcher.files = {
        "a.py": 1.0,
        "b.py": 1.0,
    }

    current = {
        "a.py": 2.0,
        "c.py": 1.0,
    }

    result = watcher.detect_changes(current)

    assert result == [
        "a.py",
        "c.py",
        "b.py",
    ]

@pytest.mark.unit
def test_watcher_forwards_changes_to_callback(tmp_path):

    calls = []

    watcher = WorkspaceWatcher(
        workspace=tmp_path,
        callback=lambda files: calls.append(files),
    )

    watcher.files = {
        "app.py": 1.0,
    }

    current = {
        "app.py": 2.0,
        "new.py": 1.0,
    }

    changed_files = watcher.detect_changes(
        current
    )

    watcher.callback(
        changed_files
    )

    assert calls == [
        [
            "app.py",
            "new.py",
        ]
    ]