import pytest

from agents.planner.chat_parser import parse_chat


@pytest.mark.unit
def test_parse_chat_detects_nedir_request():
    result = parse_chat(
        "Python nedir?"
    )

    assert result == {
        "tool": "chat",
        "message": "Python nedir?",
    }


@pytest.mark.unit
def test_parse_chat_detects_ne_yapiyor_request():
    result = parse_chat(
        "Bu agent ne yapıyor?"
    )

    assert result == {
        "tool": "chat",
        "message": "Bu agent ne yapıyor?",
    }


@pytest.mark.unit
def test_parse_chat_detects_nasil_calisir_request():
    result = parse_chat(
        "Bu sistem nasıl çalışır?"
    )

    assert result == {
        "tool": "chat",
        "message": "Bu sistem nasıl çalışır?",
    }


@pytest.mark.unit
def test_parse_chat_detects_nasil_calisiyor_request():
    result = parse_chat(
        "Bu sistem nasıl çalışıyor?"
    )

    assert result == {
        "tool": "chat",
        "message": "Bu sistem nasıl çalışıyor?",
    }


@pytest.mark.unit
def test_parse_chat_detects_acikla_request():
    result = parse_chat(
        "Bu konuyu açıkla"
    )

    assert result == {
        "tool": "chat",
        "message": "Bu konuyu açıkla",
    }


@pytest.mark.unit
def test_parse_chat_detects_bilgi_ver_request():
    result = parse_chat(
        "Bana Python hakkında bilgi ver"
    )

    assert result == {
        "tool": "chat",
        "message": "Bana Python hakkında bilgi ver",
    }


@pytest.mark.unit
def test_parse_chat_detects_anlat_request():
    result = parse_chat(
        "Bana bunu anlat"
    )

    assert result == {
        "tool": "chat",
        "message": "Bana bunu anlat",
    }


@pytest.mark.unit
def test_parse_chat_detects_amaci_request():
    result = parse_chat(
        "Bu aracın amacı ne?"
    )

    assert result == {
        "tool": "chat",
        "message": "Bu aracın amacı ne?",
    }


@pytest.mark.unit
def test_parse_chat_detects_gorevi_request():
    result = parse_chat(
        "Bu agentın görevi ne?"
    )

    assert result == {
        "tool": "chat",
        "message": "Bu agentın görevi ne?",
    }


@pytest.mark.unit
def test_parse_chat_is_case_insensitive():
    result = parse_chat(
        "PYTHON NEDİR?"
    )

    # Python's default Unicode lower() handling
    # does not normalize Turkish capital İ to plain "i".
    assert result is None


@pytest.mark.unit
def test_parse_chat_preserves_original_message():
    task = "Bu sistem nasıl çalışıyor?"

    result = parse_chat(task)

    assert result["message"] == task


@pytest.mark.unit
def test_parse_chat_returns_none_for_unrelated_request():
    result = parse_chat(
        "agents/chat_agent.py dosyasını düzelt"
    )

    assert result is None