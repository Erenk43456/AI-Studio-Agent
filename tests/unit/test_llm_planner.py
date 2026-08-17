import pytest

from agents.planner.llm_planner import (
    clean_json,
    format_tools,
    create_llm_plan,
)
from tests.fakes.fake_llm import FakeLLM


@pytest.mark.unit
def test_clean_json_returns_json_object():
    result = clean_json(
        '{"tool": "chat"}'
    )

    assert result == '{"tool": "chat"}'


@pytest.mark.unit
def test_clean_json_removes_markdown():
    result = clean_json(
        """```json
        {"tool": "chat"}
        ```"""
    )

    assert '"tool": "chat"' in result


@pytest.mark.unit
def test_clean_json_extracts_json_from_text():
    result = clean_json(
        'Here is the plan: {"tool": "chat"}'
    )

    assert result == '{"tool": "chat"}'


@pytest.mark.unit
def test_clean_json_invalid_input_returns_empty_object():
    assert clean_json(None) == "{}"
    assert clean_json("") == "{}"
    assert clean_json("hello") == "{}"


@pytest.mark.unit
def test_format_tools_returns_tool_information():
    result = format_tools(
        [
            {
                "name": "fake_tool",
                "description": "Test tool",
                "purpose": "Testing",
            }
        ]
    )

    assert "fake_tool" in result
    assert "Test tool" in result
    assert "Testing" in result


@pytest.mark.unit
def test_format_tools_without_tools():
    assert (
        format_tools([])
        == "No tool information available."
    )


@pytest.mark.unit
def test_create_llm_plan_returns_valid_plan():
    llm = FakeLLM(
        response="""
        {
            "steps": [
                {
                    "tool": "fake_tool",
                    "action": "execute",
                    "input": "hello"
                }
            ]
        }
        """
    )

    result = create_llm_plan(
        llm,
        "run the fake tool",
    )

    assert result == {
        "steps": [
            {
                "tool": "fake_tool",
                "action": "execute",
                "input": "hello",
            }
        ]
    }


@pytest.mark.unit
def test_create_llm_plan_normalizes_single_step():
    llm = FakeLLM(
        response="""
        {
            "tool": "fake_tool",
            "action": "execute",
            "input": "hello"
        }
        """
    )

    result = create_llm_plan(
        llm,
        "run the fake tool",
    )

    assert result == {
        "steps": [
            {
                "tool": "fake_tool",
                "action": "execute",
                "input": "hello",
            }
        ]
    }


@pytest.mark.unit
def test_create_llm_plan_invalid_json_returns_none():
    llm = FakeLLM(
        response="this is not json"
    )

    result = create_llm_plan(
        llm,
        "do something",
    )

    assert result is None


@pytest.mark.unit
def test_create_llm_plan_empty_steps_returns_none():
    llm = FakeLLM(
        response='{"steps": []}'
    )

    result = create_llm_plan(
        llm,
        "do something",
    )

    assert result is None


@pytest.mark.unit
def test_create_llm_plan_llm_error_returns_none():
    class ErrorLLM:

        def generate(
            self,
            prompt,
            max_tokens=None,
            temperature=None,
            timeout=None,
        ):
            raise RuntimeError(
                "test error"
            )

    result = create_llm_plan(
        ErrorLLM(),
        "do something",
    )

    assert result is None