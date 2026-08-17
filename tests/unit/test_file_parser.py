import pytest

from agents.planner.file_parser import parse_file, extract_filename


@pytest.mark.unit
def test_extract_filename():
    result = extract_filename(
        "agents/chat_agent.py dosyasını oku"
    )

    assert result == "agents/chat_agent.py"


@pytest.mark.unit
def test_extract_filename_normalizes_windows_path():
    result = extract_filename(
        r"agents\planner\chat_parser.py dosyasını oku"
    )

    assert result == "agents/planner/chat_parser.py"


@pytest.mark.unit
def test_extract_filename_returns_none_without_python_file():
    result = extract_filename(
        "agents klasörüne bak"
    )

    assert result is None


@pytest.mark.unit
def test_parse_file_create():
    result = parse_file(
        "agents/test.py dosya oluştur"
    )

    assert result == {
        "tool": "file",
        "action": "create",
        "filename": "agents/test.py",
        "content": "",
    }


@pytest.mark.unit
def test_parse_file_create_empty():
    result = parse_file(
        "agents/test.py için boş dosya oluştur"
    )

    assert result == {
        "tool": "file",
        "action": "create",
        "filename": "agents/test.py",
        "content": "",
    }


@pytest.mark.unit
def test_parse_file_read():
    result = parse_file(
        "agents/chat_agent.py dosyasını oku"
    )

    assert result == {
        "tool": "file",
        "action": "read",
        "filename": "agents/chat_agent.py",
    }


@pytest.mark.unit
def test_parse_file_show():
    result = parse_file(
        "agents/chat_agent.py dosyasının içeriğini göster"
    )

    assert result == {
        "tool": "file",
        "action": "read",
        "filename": "agents/chat_agent.py",
    }


@pytest.mark.unit
def test_parse_file_delete():
    result = parse_file(
        "agents/old_agent.py dosyayı sil"
    )

    assert result == {
        "tool": "file",
        "action": "delete",
        "filename": "agents/old_agent.py",
    }


@pytest.mark.unit
def test_parse_file_move():
    result = parse_file(
        "agents/old_agent.py dosyasını taşı"
    )

    assert result == {
        "tool": "file",
        "action": "manage",
        "filename": "agents/old_agent.py",
    }


@pytest.mark.unit
def test_parse_file_copy():
    result = parse_file(
        "agents/old_agent.py dosyasını kopyala"
    )

    assert result == {
        "tool": "file",
        "action": "manage",
        "filename": "agents/old_agent.py",
    }


@pytest.mark.unit
def test_parse_file_rejects_non_python_file():
    result = parse_file(
        "README.md dosyasını oku"
    )

    assert result is None


@pytest.mark.unit
def test_parse_file_rejects_unrelated_python_request():
    result = parse_file(
        "Python'da agents/chat_agent.py fonksiyonunu geliştir"
    )

    assert result is None