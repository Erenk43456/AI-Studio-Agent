import pytest

from agents.planner.code_parser import parse_code


@pytest.mark.unit
def test_parse_code_detects_development_request():
    result = parse_code(
        "agents/chat_agent.py dosyasını düzelt"
    )

    assert result is not None
    assert "steps" in result
    assert len(result["steps"]) == 3


@pytest.mark.unit
def test_parse_code_first_step_is_repository_analysis():
    result = parse_code(
        "agents/chat_agent.py dosyasını düzelt"
    )

    assert result["steps"][0] == {
        "tool": "repository_analyzer",
        "action": "analyze",
        "input": "agents/chat_agent.py dosyasını düzelt",
    }


@pytest.mark.unit
def test_parse_code_second_step_is_code_analysis():
    result = parse_code(
        "agents/chat_agent.py dosyasını düzelt"
    )

    assert result["steps"][1] == {
        "tool": "code_analyzer",
        "action": "analyze",
        "input": "agents/chat_agent.py dosyasını düzelt",
    }


@pytest.mark.unit
def test_parse_code_third_step_is_implementation():
    result = parse_code(
        "agents/chat_agent.py dosyasını düzelt"
    )

    assert result["steps"][2] == {
        "tool": "code",
        "action": "implement",
        "input": "agents/chat_agent.py dosyasını düzelt",
    }


@pytest.mark.unit
def test_parse_code_detects_add_request():
    result = parse_code(
        "agents/chat_agent.py dosyasına yeni özellik ekle"
    )

    assert result is not None
    assert len(result["steps"]) == 3
    assert result["steps"][-1]["tool"] == "code"


@pytest.mark.unit
def test_parse_code_detects_refactor_request():
    result = parse_code(
        "agents/chat_agent.py dosyasını refactor et"
    )

    assert result is not None
    assert result["steps"][-1]["action"] == "implement"


@pytest.mark.unit
def test_parse_code_detects_architecture_request():
    result = parse_code(
        "AI agent mimarisini genişlet"
    )

    assert result is not None
    assert len(result["steps"]) == 3


@pytest.mark.unit
def test_parse_code_rejects_analysis_request():
    result = parse_code(
        "agents/chat_agent.py ne yapıyor"
    )

    assert result is None


@pytest.mark.unit
def test_parse_code_rejects_explanation_request():
    result = parse_code(
        "agents/chat_agent.py nasıl çalışır"
    )

    assert result is None


@pytest.mark.unit
def test_parse_code_rejects_unrelated_message():
    result = parse_code(
        "Bugün hava çok güzel"
    )

    assert result is None


@pytest.mark.unit
def test_parse_code_accepts_python_file_target():
    result = parse_code(
        "agents/chat_agent.py"
    )

    assert result is not None
    assert len(result["steps"]) == 3
    assert result["steps"][-1]["tool"] == "code"


@pytest.mark.unit
def test_parse_code_is_case_insensitive():
    result = parse_code(
        "AGENTS/CHAT_AGENT.PY DOSYASINI DÜZELT"
    )

    assert result is not None
    assert len(result["steps"]) == 3