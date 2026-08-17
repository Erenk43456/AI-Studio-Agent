import pytest

from tools.code_analyzer_tool import CodeAnalyzerTool

from tests.fakes.fake_llm import FakeLLM


@pytest.mark.unit
def test_code_analyzer_execute_analyzes_plain_string():
    llm = FakeLLM(
        response={
            "summary": "Looks good",
            "syntax_errors": [],
            "logical_errors": [],
            "security_issues": [],
            "performance_issues": [],
            "architecture_issues": [],
            "improvements": [],
            "risk_level": "low",
        }
    )

    analyzer = CodeAnalyzerTool(
        llm=llm,
    )

    result = analyzer.execute(
        "print('hello')"
    )

    assert result["success"] is True

    assert result["analysis"] == {
        "summary": "Looks good",
        "syntax_errors": [],
        "logical_errors": [],
        "security_issues": [],
        "performance_issues": [],
        "architecture_issues": [],
        "improvements": [],
        "risk_level": "low",
    }


@pytest.mark.unit
def test_code_analyzer_execute_uses_code_from_plan():
    llm = FakeLLM(
        response='{"summary": "OK"}'
    )

    analyzer = CodeAnalyzerTool(
        llm=llm,
    )

    result = analyzer.execute(
        {
            "code": "print('hello')",
        }
    )

    assert result["success"] is True

    assert result["analysis"] == {
        "summary": "OK",
    }


@pytest.mark.unit
def test_code_analyzer_execute_uses_context_when_code_missing():
    llm = FakeLLM(
        response='{"summary": "Context analyzed"}'
    )

    analyzer = CodeAnalyzerTool(
        llm=llm,
    )

    result = analyzer.execute(
        {
            "context": "def hello():\n    return 1",
        }
    )

    assert result["success"] is True

    assert result["analysis"] == {
        "summary": "Context analyzed",
    }


@pytest.mark.unit
def test_code_analyzer_execute_uses_content_when_code_and_context_missing():
    llm = FakeLLM(
        response='{"summary": "Content analyzed"}'
    )

    analyzer = CodeAnalyzerTool(
        llm=llm,
    )

    result = analyzer.execute(
        {
            "content": "x = 1",
        }
    )

    assert result["success"] is True

    assert result["analysis"] == {
        "summary": "Content analyzed",
    }


@pytest.mark.unit
def test_code_analyzer_returns_file_not_found():
    from pathlib import Path

    workspace = Path(
        "tests"
    )

    analyzer = CodeAnalyzerTool(
        llm=FakeLLM(),
        workspace=workspace,
    )

    result = analyzer.execute(
        {
            "filename": "does_not_exist.py",
        }
    )

    assert result == {
        "success": False,
        "error": "File not found",
        "file": "does_not_exist.py",
    }


@pytest.mark.unit
def test_code_analyzer_reads_file_from_workspace(
    tmp_path,
):
    source = tmp_path / "parser.py"

    source.write_text(
        "class Parser:\n    pass\n",
        encoding="utf-8",
    )

    llm = FakeLLM(
        response='{"summary": "Parser analyzed"}'
    )

    analyzer = CodeAnalyzerTool(
        llm=llm,
        workspace=tmp_path,
    )

    result = analyzer.execute(
        {
            "filename": "parser.py",
        }
    )

    assert result["success"] is True

    assert result["analysis"] == {
        "summary": "Parser analyzed",
    }

    assert result["file"] == str(
        source
    )


@pytest.mark.unit
def test_code_analyzer_empty_code_returns_failure():
    analyzer = CodeAnalyzerTool(
        llm=FakeLLM(),
    )

    result = analyzer.analyze_code(
        ""
    )

    assert result == {
        "success": False,
        "error": "Code is empty.",
    }


@pytest.mark.unit
def test_code_analyzer_whitespace_only_code_is_not_empty():
    llm = FakeLLM(
        response='{"summary": "Analyzed"}'
    )

    analyzer = CodeAnalyzerTool(
        llm=llm,
    )

    result = analyzer.analyze_code(
        "   "
    )

    assert result["success"] is True


@pytest.mark.unit
def test_code_analyzer_truncates_large_code():
    class CapturingLLM:
        def __init__(self):
            self.prompt = None

        def generate(
            self,
            prompt,
            max_tokens=None,
            temperature=None,
            timeout=None,
        ):
            self.prompt = prompt

            return '{"summary": "Large file analyzed"}'

    llm = CapturingLLM()

    analyzer = CodeAnalyzerTool(
        llm=llm,
    )

    code = "x = 1\n" * 3000

    assert len(code) > analyzer.max_code_length

    result = analyzer.analyze_code(
        code
    )

    assert result["success"] is True

    assert (
        len(llm.prompt)
        <
        len(code) + 1000
    )

    assert (
        code[:analyzer.max_code_length]
        in llm.prompt
    )


@pytest.mark.unit
def test_code_analyzer_handles_empty_llm_response():
    analyzer = CodeAnalyzerTool(
        llm=FakeLLM(
            response=""
        ),
    )

    result = analyzer.analyze_code(
        "print('hello')"
    )

    assert result == {
        "success": False,
        "error": "Empty LLM response.",
    }


@pytest.mark.unit
def test_code_analyzer_handles_llm_error_string():
    analyzer = CodeAnalyzerTool(
        llm=FakeLLM(
            response="LLM_ERROR: model unavailable"
        ),
    )

    result = analyzer.analyze_code(
        "print('hello')"
    )

    assert result == {
        "success": False,
        "error": "LLM_ERROR: model unavailable",
    }


@pytest.mark.unit
def test_code_analyzer_handles_llm_error_dict():
    analyzer = CodeAnalyzerTool(
        llm=FakeLLM(
            response={
                "error": "model unavailable"
            }
        ),
    )

    result = analyzer.analyze_code(
        "print('hello')"
    )

    assert result == {
        "success": False,
        "error": "model unavailable",
    }


@pytest.mark.unit
def test_code_analyzer_handles_llm_exception():
    class ExplodingLLM:
        def generate(
            self,
            prompt,
            max_tokens=None,
            temperature=None,
            timeout=None,
        ):
            raise RuntimeError(
                "LLM unavailable"
            )

    analyzer = CodeAnalyzerTool(
        llm=ExplodingLLM(),
    )

    result = analyzer.analyze_code(
        "print('hello')"
    )

    assert result == {
        "success": False,
        "error": "LLM unavailable",
    }

@pytest.mark.unit
def test_code_analyzer_clean_json_parses_plain_json():
    analyzer = CodeAnalyzerTool(
        llm=FakeLLM()
    )

    result = analyzer.clean_json(
        '{"summary": "OK", "risk_level": "low"}'
    )

    assert result == {
        "summary": "OK",
        "risk_level": "low",
    }


@pytest.mark.unit
def test_code_analyzer_clean_json_removes_json_markdown():
    analyzer = CodeAnalyzerTool(
        llm=FakeLLM()
    )

    result = analyzer.clean_json(
        """```json
{
    "summary": "OK",
    "risk_level": "low"
}
```"""
    )

    assert result == {
        "summary": "OK",
        "risk_level": "low",
    }


@pytest.mark.unit
def test_code_analyzer_clean_json_removes_plain_code_fence():
    analyzer = CodeAnalyzerTool(
        llm=FakeLLM()
    )

    result = analyzer.clean_json(
        """```
{
    "summary": "OK"
}
```"""
    )

    assert result == {
        "summary": "OK",
    }


@pytest.mark.unit
def test_code_analyzer_clean_json_extracts_json_from_extra_text():
    analyzer = CodeAnalyzerTool(
        llm=FakeLLM()
    )

    result = analyzer.clean_json(
        """
        Here is the analysis:

        {
            "summary": "Looks good",
            "risk_level": "low"
        }

        End of analysis.
        """
    )

    assert result == {
        "summary": "Looks good",
        "risk_level": "low",
    }


@pytest.mark.unit
def test_code_analyzer_clean_json_returns_parse_error_for_invalid_json():
    analyzer = CodeAnalyzerTool(
        llm=FakeLLM()
    )

    result = analyzer.clean_json(
        '{"summary": "broken",}'
    )

    assert result == {
        "raw_response": '{"summary": "broken",}',
        "parse_error": True,
    }


@pytest.mark.unit
def test_code_analyzer_clean_json_returns_empty_object_for_empty_text():
    analyzer = CodeAnalyzerTool(
        llm=FakeLLM()
    )

    result = analyzer.clean_json(
        ""
    )

    assert result == "{}"


@pytest.mark.unit
def test_code_analyzer_clean_json_accepts_dict():
    analyzer = CodeAnalyzerTool(
        llm=FakeLLM()
    )

    value = {
        "summary": "Already parsed",
        "risk_level": "low",
    }

    result = analyzer.clean_json(
        value
    )

    assert result is value


@pytest.mark.unit
def test_code_analyzer_clean_json_handles_json_with_nested_objects():
    analyzer = CodeAnalyzerTool(
        llm=FakeLLM()
    )

    result = analyzer.clean_json(
        """
        {
            "summary": "Nested",
            "details": {
                "security": {
                    "severity": "low"
                }
            }
        }
        """
    )

    assert result == {
        "summary": "Nested",
        "details": {
            "security": {
                "severity": "low"
            }
        },
    }


@pytest.mark.unit
def test_code_analyzer_analyze_code_returns_parsed_markdown_json():
    analyzer = CodeAnalyzerTool(
        llm=FakeLLM(
            response="""```json
{
    "summary": "Parser is valid",
    "syntax_errors": [],
    "risk_level": "low"
}
```"""
        )
    )

    result = analyzer.analyze_code(
        "class Parser:\n    pass\n"
    )

    assert result == {
        "success": True,
        "analysis": {
            "summary": "Parser is valid",
            "syntax_errors": [],
            "risk_level": "low",
        },
    }


@pytest.mark.unit
def test_code_analyzer_analyze_code_preserves_unparseable_response():
    response = (
        "This is not valid JSON."
    )

    analyzer = CodeAnalyzerTool(
        llm=FakeLLM(
            response=response
        )
    )

    result = analyzer.analyze_code(
        "print('hello')"
    )

    assert result == {
        "success": True,
        "analysis": {
            "raw_response": response,
            "parse_error": True,
        },
    }

@pytest.mark.unit
def test_code_analyzer_plan_prefers_code_over_context_and_content():
    llm = FakeLLM(
        response='{"summary": "Code selected"}'
    )

    analyzer = CodeAnalyzerTool(
        llm=llm,
    )

    result = analyzer.execute(
        {
            "code": "CODE",
            "context": "CONTEXT",
            "content": "CONTENT",
        }
    )

    assert result["success"] is True
    assert result["analysis"] == {
        "summary": "Code selected",
    }


@pytest.mark.unit
def test_code_analyzer_plan_prefers_context_over_content():
    llm = FakeLLM(
        response='{"summary": "Context selected"}'
    )

    analyzer = CodeAnalyzerTool(
        llm=llm,
    )

    result = analyzer.execute(
        {
            "context": "CONTEXT",
            "content": "CONTENT",
        }
    )

    assert result["success"] is True
    assert result["analysis"] == {
        "summary": "Context selected",
    }


@pytest.mark.unit
def test_code_analyzer_plan_uses_content_as_last_fallback():
    llm = FakeLLM(
        response='{"summary": "Content selected"}'
    )

    analyzer = CodeAnalyzerTool(
        llm=llm,
    )

    result = analyzer.execute(
        {
            "content": "CONTENT",
        }
    )

    assert result["success"] is True
    assert result["analysis"] == {
        "summary": "Content selected",
    }


@pytest.mark.unit
def test_code_analyzer_empty_plan_returns_empty_code_error():
    analyzer = CodeAnalyzerTool(
        llm=FakeLLM(),
    )

    result = analyzer.execute({})

    assert result == {
        "success": False,
        "error": "Code is empty.",
    }


@pytest.mark.unit
def test_code_analyzer_filename_without_workspace_falls_back_to_empty_code():
    analyzer = CodeAnalyzerTool(
        llm=FakeLLM(),
        workspace=None,
    )

    result = analyzer.execute(
        {
            "filename": "parser.py",
        }
    )

    assert result == {
        "success": False,
        "error": "Code is empty.",
    }


@pytest.mark.unit
def test_code_analyzer_accepts_numeric_plan():
    llm = FakeLLM(
        response='{"summary": "Numeric input analyzed"}'
    )

    analyzer = CodeAnalyzerTool(
        llm=llm,
    )

    result = analyzer.execute(12345)

    assert result["success"] is True
    assert result["analysis"] == {
        "summary": "Numeric input analyzed",
    }


@pytest.mark.unit
def test_code_analyzer_accepts_list_plan():
    llm = FakeLLM(
        response='{"summary": "List input analyzed"}'
    )

    analyzer = CodeAnalyzerTool(
        llm=llm,
    )

    result = analyzer.execute(
        ["print('hello')"]
    )

    assert result["success"] is True
    assert result["analysis"] == {
        "summary": "List input analyzed",
    }


@pytest.mark.unit
def test_code_analyzer_exact_max_code_length_is_not_truncated():
    class CapturingLLM:
        def __init__(self):
            self.prompt = None

        def generate(
            self,
            prompt,
            max_tokens=None,
            temperature=None,
            timeout=None,
        ):
            self.prompt = prompt
            return '{"summary": "OK"}'

    llm = CapturingLLM()

    analyzer = CodeAnalyzerTool(
        llm=llm,
    )

    code = "x" * analyzer.max_code_length

    result = analyzer.analyze_code(code)

    assert result["success"] is True

    assert (
        code in llm.prompt
    )


@pytest.mark.unit
def test_code_analyzer_over_max_code_length_is_truncated():
    class CapturingLLM:
        def __init__(self):
            self.prompt = None

        def generate(
            self,
            prompt,
            max_tokens=None,
            temperature=None,
            timeout=None,
        ):
            self.prompt = prompt
            return '{"summary": "OK"}'

    llm = CapturingLLM()

    analyzer = CodeAnalyzerTool(
        llm=llm,
    )

    code = "x" * (
        analyzer.max_code_length + 1
    )

    result = analyzer.analyze_code(code)

    assert result["success"] is True

    assert (
        "x" * analyzer.max_code_length
        in llm.prompt
    )