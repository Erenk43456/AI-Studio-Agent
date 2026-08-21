import pytest

from tools.code_repair_tool import CodeRepairTool

from tests.fakes.fake_llm import FakeLLM


@pytest.mark.unit
def test_code_repair_repairs_valid_python():
    llm = FakeLLM(
        response="""\
def hello():
    return "fixed"
"""
    )

    repair = CodeRepairTool(
        llm=llm,
    )

    result = repair.repair_code(
        "def hello(\n    return 'broken'",
        "Fix the syntax error",
    )

    assert result["success"] is True
    assert result["code"] == """\
def hello():
    return 'fixed'
"""


@pytest.mark.unit
def test_code_repair_rejects_non_string_code():
    repair = CodeRepairTool(
        llm=FakeLLM(),
    )

    result = repair.repair_code(
        123,
        "Fix it",
    )

    assert result == {
        "success": False,
        "message": "Invalid code input.",
    }


@pytest.mark.unit
def test_code_repair_rejects_empty_code():
    repair = CodeRepairTool(
        llm=FakeLLM(),
    )

    result = repair.repair_code(
        "   ",
        "Fix it",
    )

    assert result == {
        "success": False,
        "message": "Code is empty.",
    }


@pytest.mark.unit
def test_code_repair_handles_llm_exception():
    class ExplodingLLM:
        def generate(self, prompt):
            raise RuntimeError(
                "model unavailable"
            )

    repair = CodeRepairTool(
        llm=ExplodingLLM(),
    )

    result = repair.repair_code(
        "def broken(:\n    pass",
        "Fix syntax",
    )

    assert result == {
        "success": False,
        "message": (
            "LLM repair failed: "
            "model unavailable"
        ),
    }


@pytest.mark.unit
def test_code_repair_handles_llm_dict_response():
    repair = CodeRepairTool(
        llm=FakeLLM(
            response={
                "error": "generation failed"
            }
        ),
    )

    result = repair.repair_code(
        "def broken(:\n    pass",
        "Fix syntax",
    )

    assert result == {
        "success": False,
        "message": (
            "LLM returned an error: "
            "{'error': 'generation failed'}"
        ),
    }


@pytest.mark.unit
def test_code_repair_handles_invalid_llm_response_type():
    repair = CodeRepairTool(
        llm=FakeLLM(
            response=12345
        ),
    )

    result = repair.repair_code(
        "def broken(:\n    pass",
        "Fix syntax",
    )

    assert result == {
        "success": False,
        "message": (
            "LLM returned an invalid response type."
        ),
    }


@pytest.mark.unit
def test_code_repair_handles_empty_llm_response():
    repair = CodeRepairTool(
        llm=FakeLLM(
            response="   "
        ),
    )

    result = repair.repair_code(
        "def broken(:\n    pass",
        "Fix syntax",
    )

    assert result == {
        "success": False,
        "message": (
            "LLM returned empty repaired code."
        ),
    }


@pytest.mark.unit
def test_code_repair_rejects_invalid_repaired_python():
    repair = CodeRepairTool(
        llm=FakeLLM(
            response="""\
def broken(
    pass
"""
        ),
    )

    result = repair.repair_code(
        "def broken(:\n    pass",
        "Fix syntax",
    )

    assert result["success"] is False
    assert result["message"] == (
        "Code repair returned invalid code."
    )
    assert "details" in result


@pytest.mark.unit
def test_code_repair_clean_code_removes_markdown_fence():
    result = CodeRepairTool.clean_code(
        """```python
def hello():
    return "hello"
```"""
    )

    assert result == """\
def hello():
    return "hello"
"""


@pytest.mark.unit
def test_code_repair_clean_code_adds_trailing_newline():
    result = CodeRepairTool.clean_code(
        "def hello():\n    pass"
    )

    assert result == """\
def hello():
    pass
"""


@pytest.mark.unit
def test_code_repair_clean_code_handles_empty_value():
    assert CodeRepairTool.clean_code(
        ""
    ) == ""

    assert CodeRepairTool.clean_code(
        None
    ) == ""


@pytest.mark.unit
def test_code_repair_validate_python_accepts_valid_code():
    result = CodeRepairTool.validate_python(
        "def hello():\n    return 1\n"
    )

    assert result is None


@pytest.mark.unit
def test_code_repair_validate_python_reports_syntax_error():
    result = CodeRepairTool.validate_python(
        "def hello(\n    return 1\n"
    )

    assert result is not None
    assert "line" in result
    assert "column" in result

@pytest.mark.unit
def test_code_repair_execute_repairs_file_successfully(tmp_path):
    source = tmp_path / "parser.py"

    source.write_text(
        "def broken(:\n    pass\n",
        encoding="utf-8",
    )

    llm = FakeLLM(
        response="""\
def parser():
    return 42
"""
    )

    repair = CodeRepairTool(
        llm=llm,
        workspace=tmp_path,
    )

    result = repair.execute(
        {
            "filename": "parser.py",
            "context": "Fix the parser syntax",
        }
    )

    assert result["success"] is True
    assert result["file"] == str(source)

    assert source.read_text(
        encoding="utf-8"
    ) == """\
def parser():
    return 42
"""


@pytest.mark.unit
def test_code_repair_execute_returns_file_error_when_file_missing(
    tmp_path,
):
    repair = CodeRepairTool(
        llm=FakeLLM(),
        workspace=tmp_path,
    )

    result = repair.execute(
        {
            "filename": "missing.py",
            "context": "Repair it",
        }
    )

    assert result["success"] is False
    assert result["file"] == "missing.py"
    assert "message" in result


@pytest.mark.unit
def test_code_repair_execute_does_not_write_when_repair_fails(
    tmp_path,
):
    source = tmp_path / "parser.py"

    original = """\
def broken(:
    pass
"""

    source.write_text(
        original,
        encoding="utf-8",
    )

    repair = CodeRepairTool(
        llm=FakeLLM(
            response="def broken(:\n    pass"
        ),
        workspace=tmp_path,
    )

    result = repair.execute(
        {
            "filename": "parser.py",
            "context": "Fix syntax",
        }
    )

    assert result["success"] is False

    assert source.read_text(
        encoding="utf-8"
    ) == original


@pytest.mark.unit
def test_code_repair_execute_uses_supplied_code_before_file(
    tmp_path,
):
    source = tmp_path / "parser.py"

    source.write_text(
        """\
def old():
    return 1
""",
        encoding="utf-8",
    )

    llm = FakeLLM(
        response="""\
def supplied():
    return 2
"""
    )

    repair = CodeRepairTool(
        llm=llm,
        workspace=tmp_path,
    )

    result = repair.execute(
        {
            "filename": "parser.py",
            "code": """\
def broken(:
    return 2
""",
            "context": "Repair supplied code",
        }
    )

    assert result["success"] is True
    assert result["file"] == "parser.py"

    # Supplied code is repaired and returned,
    # but direct supplied-code mode does not write
    # the file automatically.
    assert source.read_text(
        encoding="utf-8"
    ) == """\
def old():
    return 1
"""


@pytest.mark.unit
def test_code_repair_execute_uses_input_as_supplied_code():
    llm = FakeLLM(
        response="""\
def fixed():
    return True
"""
    )

    repair = CodeRepairTool(
        llm=llm,
    )

    result = repair.execute(
        {
            "input": """\
def broken(:
    return True
""",
            "context": "Fix syntax",
        }
    )

    assert result["success"] is True
    assert result["code"] == """\
def fixed():
    return True
"""


@pytest.mark.unit
def test_code_repair_execute_returns_repair_result_for_plain_string():
    llm = FakeLLM(
        response="""\
def fixed():
    return 1
"""
    )

    repair = CodeRepairTool(
        llm=llm,
    )

    result = repair.execute(
        """\
def broken(:
    return 1
"""
    )

    assert result == {
        "success": True,
        "code": """\
def fixed():
    return 1
""",
    }


@pytest.mark.unit
def test_code_repair_execute_uses_context_as_code_fallback():
    llm = FakeLLM(
        response="""\
def fixed():
    return 5
"""
    )

    repair = CodeRepairTool(
        llm=llm,
    )

    result = repair.execute(
        {
            "context": """\
def broken(:
    return 5
""",
        }
    )

    assert result["success"] is True
    assert result["code"] == """\
def fixed():
    return 5
"""


@pytest.mark.unit
def test_code_repair_execute_supplied_code_adds_filename_to_success():
    llm = FakeLLM(
        response="""\
def fixed():
    return 10
"""
    )

    repair = CodeRepairTool(
        llm=llm,
    )

    result = repair.execute(
        {
            "filename": "parser.py",
            "code": """\
def broken(:
    return 10
""",
        }
    )

    assert result["success"] is True
    assert result["file"] == "parser.py"


@pytest.mark.unit
def test_code_repair_execute_without_workspace_does_not_read_file():
    repair = CodeRepairTool(
        llm=FakeLLM(),
        workspace=None,
    )

    result = repair.execute(
        {
            "filename": "parser.py",
        }
    )

    assert result == {
        "success": False,
        "message": "Code is empty.",
    }

@pytest.mark.unit
def test_code_repair_retries_when_first_generated_code_is_invalid():
    invalid_code = """\
def calculate_product(a: int, b: int) -> int:
    return a * b
    print("broken
"""

    valid_code = """\
def calculate_product(a: int, b: int) -> int:
    return a * b
"""

    class FakeLLM:
        def __init__(self):
            self.calls = 0

        def generate(self, prompt):
            self.calls += 1

            if self.calls == 1:
                return invalid_code

            return valid_code

    tool = CodeRepairTool(
        llm=FakeLLM()
    )

    result = tool.execute({
        "code": invalid_code,
        "context": "Repair the syntax error."
    })

    assert result["success"] is True
    assert "calculate_product" in result["code"]