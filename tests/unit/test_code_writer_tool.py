import pytest

from tools.code_writer_tool import CodeWriterTool


class FakeLLM:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def generate(self, prompt):
        self.calls.append(prompt)

        if self.error:
            raise self.error

        return self.response


class FakeRegistry:
    def __init__(self, tools=None):
        self.tools = tools or {}
        self.calls = []

    def get(self, name):
        self.calls.append(name)
        return self.tools.get(name)

class SequentialFakeLLM:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def generate(self, prompt):
        self.calls.append(prompt)
        return self.responses.pop(0)


@pytest.fixture
def valid_code():
    return """\
class Parser:
    def parse(self, value):
        return value
"""


@pytest.fixture
def writer(tmp_path):
    return CodeWriterTool(
        llm=FakeLLM(),
        workspace=tmp_path,
    )


@pytest.mark.unit
def test_code_writer_metadata(writer):
    assert writer.name == "code_writer"
    assert writer.description
    assert writer.purpose
    assert writer.safe is False
    assert writer.modifies_files is True
    assert writer.requires_confirmation is True
    assert writer.version == "1.3"


@pytest.mark.unit
def test_code_writer_execute_rejects_non_dict(writer):
    result = writer.execute(
        "invalid plan"
    )

    assert result == {
        "success": False,
        "message": "Invalid plan.",
    }


@pytest.mark.unit
def test_code_writer_execute_rejects_invalid_files_list(
    writer,
):
    result = writer.execute(
        {
            "files": "not a list",
        }
    )

    assert result == {
        "success": False,
        "message": "Invalid files list.",
    }


@pytest.mark.unit
def test_code_writer_execute_returns_failure_for_empty_files(
    writer,
):
    result = writer.execute(
        {
            "files": [],
        }
    )

    assert result == {
        "success": False,
        "message": "No valid files were provided.",
        "results": [],
    }


@pytest.mark.unit
def test_code_writer_execute_ignores_invalid_file_entries(
    writer,
):
    result = writer.execute(
        {
            "files": [
                "invalid",
                {},
                {
                    "path": "",
                    "changes": [],
                },
            ],
        }
    )

    assert result == {
        "success": False,
        "message": "No valid files were provided.",
        "results": [],
    }


@pytest.mark.unit
def test_code_writer_execute_stores_development_context(
    tmp_path,
    valid_code,
):
    llm = FakeLLM(
        response=valid_code
    )

    writer = CodeWriterTool(
        llm=llm,
        workspace=tmp_path,
    )

    source = tmp_path / "parser.py"
    source.write_text(
        valid_code,
        encoding="utf-8",
    )

    context = {
        "task": "Improve parser",
        "strategy": {
            "type": "development",
        },
    }

    result = writer.execute(
        {
            "development_context": context,
            "files": [
                {
                    "path": "parser.py",
                    "changes": [
                        "Improve parsing",
                    ],
                },
            ],
        }
    )

    assert result["success"] is True
    assert writer.current_development_context == context


@pytest.mark.unit
def test_code_writer_modify_file_requires_workspace():
    writer = CodeWriterTool(
        llm=FakeLLM(),
        workspace=None,
    )

    result = writer.modify_file(
        "parser.py",
        ["Improve parser"],
    )

    assert result == {
        "file": "parser.py",
        "error": "Workspace is not configured.",
    }


@pytest.mark.unit
def test_code_writer_rejects_path_outside_workspace(
    writer,
):
    result = writer.modify_file(
        "../parser.py",
        ["Modify parser"],
    )

    assert result == {
        "file": "../parser.py",
        "error": "Path is outside the workspace.",
    }


@pytest.mark.unit
def test_code_writer_returns_file_not_found(
    writer,
):
    result = writer.modify_file(
        "missing.py",
        ["Modify parser"],
    )

    assert result == {
        "file": "missing.py",
        "error": "File not found.",
    }


@pytest.mark.unit
def test_code_writer_rejects_directory_target(
    writer,
    tmp_path,
):
    directory = tmp_path / "parser.py"
    directory.mkdir()

    result = writer.modify_file(
        "parser.py",
        ["Modify parser"],
    )

    assert result == {
        "file": "parser.py",
        "error": "Target is not a file.",
    }


@pytest.mark.unit
def test_code_writer_returns_llm_exception(
    tmp_path,
    valid_code,
):
    llm = FakeLLM(
        error=RuntimeError(
            "LLM unavailable"
        )
    )

    writer = CodeWriterTool(
        llm=llm,
        workspace=tmp_path,
    )

    source = tmp_path / "parser.py"
    source.write_text(
        valid_code,
        encoding="utf-8",
    )

    result = writer.modify_file(
        "parser.py",
        ["Improve parser"],
    )

    assert result == {
        "file": "parser.py",
        "error": (
            "Code generation failed: "
            "LLM unavailable"
        ),
    }


@pytest.mark.unit
def test_code_writer_rejects_invalid_llm_response_type(
    tmp_path,
    valid_code,
):
    llm = FakeLLM(
        response={
            "error": "generation failed",
        }
    )

    writer = CodeWriterTool(
        llm=llm,
        workspace=tmp_path,
    )

    source = tmp_path / "parser.py"
    source.write_text(
        valid_code,
        encoding="utf-8",
    )

    result = writer.modify_file(
        "parser.py",
        ["Improve parser"],
    )

    assert result == {
        "file": "parser.py",
        "error": {
            "error": "generation failed",
        },
    }


@pytest.mark.unit
def test_code_writer_rejects_non_string_llm_response(
    tmp_path,
    valid_code,
):
    llm = FakeLLM(
        response=12345
    )

    writer = CodeWriterTool(
        llm=llm,
        workspace=tmp_path,
    )

    source = tmp_path / "parser.py"
    source.write_text(
        valid_code,
        encoding="utf-8",
    )

    result = writer.modify_file(
        "parser.py",
        ["Improve parser"],
    )

    assert result == {
        "file": "parser.py",
        "error": (
            "LLM returned an invalid response type."
        ),
    }


@pytest.mark.unit
def test_code_writer_rejects_empty_generated_code(
    tmp_path,
    valid_code,
):
    llm = FakeLLM(
        response="   \n\t"
    )

    writer = CodeWriterTool(
        llm=llm,
        workspace=tmp_path,
    )

    source = tmp_path / "parser.py"
    source.write_text(
        valid_code,
        encoding="utf-8",
    )

    result = writer.modify_file(
        "parser.py",
        ["Improve parser"],
    )

    assert result == {
        "file": "parser.py",
        "error": "LLM returned empty code.",
    }


@pytest.mark.unit
def test_code_writer_successfully_updates_file(
    tmp_path,
):
    original = """\
class Parser:
    def parse(self, value):
        return value
"""

    generated = """\
class Parser:
    def parse(self, value):
        return value.strip()
"""

    source = tmp_path / "parser.py"

    source.write_text(
        original,
        encoding="utf-8",
    )

    llm = FakeLLM(
        response=generated
    )

    writer = CodeWriterTool(
        llm=llm,
        workspace=tmp_path,
    )

    result = writer.modify_file(
        "parser.py",
        ["Strip parser input"],
    )

    assert result == {
        "file": "parser.py",
        "status": "updated",
    }

    written = source.read_text(
        encoding="utf-8"
    )

    assert "class Parser:" in written
    assert "def parse(self, value):" in written
    assert "return value.strip()" in written
    assert written != original

    assert len(llm.calls) == 1


@pytest.mark.unit
def test_code_writer_execute_successfully_updates_multiple_files(
    tmp_path,
):
    source_a = tmp_path / "a.py"
    source_b = tmp_path / "b.py"

    original_a = """\
class A:
    def run(self):
        return 1
"""

    original_b = """\
class B:
    def run(self):
        return 2
"""

    generated_a = """\
class A:
    def run(self):
        return 10
"""

    generated_b = """\
class B:
    def run(self):
        return 20
"""

    source_a.write_text(
        original_a,
        encoding="utf-8",
    )

    source_b.write_text(
        original_b,
        encoding="utf-8",
    )

    llm = SequentialFakeLLM(
        [
            generated_a,
            generated_b,
        ]
    )

    writer = CodeWriterTool(
        llm=llm,
        workspace=tmp_path,
    )

    # LLM fake'i aynı response'u döndürüyor.
    # İki dosyanın da kendi architecture contract'ı korunuyor.
    result = writer.execute(
        {
            "files": [
                {
                    "path": "a.py",
                    "changes": [
                        "Update A",
                    ],
                },
                {
                    "path": "b.py",
                    "changes": [
                        "Update B",
                    ],
                },
            ],
        }
    )

    assert result["success"] is True
    assert len(result["results"]) == 2

    assert all(
        item["status"] == "updated"
        for item in result["results"]
    )

@pytest.mark.unit
def test_code_writer_repairs_invalid_python(
    tmp_path,
):
    original = """\
class Parser:
    def parse(self, value):
        return value
"""

    broken = """\
class Parser:
    def parse(self, value)
        return value.strip()
"""

    repaired = """\
class Parser:
    def parse(self, value):
        return value.strip()
"""

    source = tmp_path / "parser.py"
    source.write_text(
        original,
        encoding="utf-8",
    )

    class FakeRepairTool:
        def __init__(self):
            self.calls = []

        def execute(self, request):
            self.calls.append(request)

            return {
                "success": True,
                "code": repaired,
            }

    repair_tool = FakeRepairTool()

    registry = FakeRegistry(
        {
            "code_repair": repair_tool,
        }
    )

    writer = CodeWriterTool(
        llm=FakeLLM(
            response=broken
        ),
        workspace=tmp_path,
        registry=registry,
    )

    result = writer.modify_file(
        "parser.py",
        ["Fix parser validation"],
    )

    assert result == {
        "file": "parser.py",
        "status": "updated",
    }

    assert len(repair_tool.calls) == 1

    assert repair_tool.calls[0]["filename"] == (
        "parser.py"
    )

    assert repair_tool.calls[0]["code"] == broken

    assert "Repair" in (
        repair_tool.calls[0]["context"]
    )

    assert (
        "return value.strip()"
        in source.read_text(
            encoding="utf-8"
        )
    )


@pytest.mark.unit
def test_code_writer_returns_failure_when_syntax_repair_fails(
    tmp_path,
):
    original = """\
class Parser:
    def parse(self, value):
        return value
"""

    broken = """\
class Parser:
    def parse(self, value)
        return value
"""

    source = tmp_path / "parser.py"
    source.write_text(
        original,
        encoding="utf-8",
    )

    class FailingRepairTool:
        def execute(self, request):
            return {
                "success": False,
                "error": "Unable to repair",
            }

    writer = CodeWriterTool(
        llm=FakeLLM(
            response=broken
        ),
        workspace=tmp_path,
        registry=FakeRegistry(
            {
                "code_repair": FailingRepairTool(),
            }
        ),
    )

    result = writer.modify_file(
        "parser.py",
        ["Fix syntax"],
    )

    assert result["file"] == "parser.py"

    assert result["error"] == (
        "Generated code has invalid Python syntax "
        "and automatic repair failed."
    )

    assert "details" in result

    assert source.read_text(
        encoding="utf-8"
    ) == original


@pytest.mark.unit
def test_code_writer_syntax_repair_requires_registry(
    tmp_path,
):
    original = """\
class Parser:
    def parse(self, value):
        return value
"""

    broken = """\
class Parser:
    def parse(self, value)
        return value
"""

    source = tmp_path / "parser.py"
    source.write_text(
        original,
        encoding="utf-8",
    )

    writer = CodeWriterTool(
        llm=FakeLLM(
            response=broken
        ),
        workspace=tmp_path,
    )

    result = writer.modify_file(
        "parser.py",
        ["Fix syntax"],
    )

    assert result["error"] == (
        "Generated code has invalid Python syntax "
        "and automatic repair failed."
    )

    assert source.read_text(
        encoding="utf-8"
    ) == original


@pytest.mark.unit
def test_code_writer_rejects_removed_class(
    tmp_path,
):
    original = """\
class Parser:
    def parse(self, value):
        return value
"""

    generated = """\
class Other:
    def run(self):
        return 1
"""

    source = tmp_path / "parser.py"
    source.write_text(
        original,
        encoding="utf-8",
    )

    writer = CodeWriterTool(
        llm=FakeLLM(
            response=generated
        ),
        workspace=tmp_path,
    )

    result = writer.modify_file(
        "parser.py",
        ["Replace parser"],
    )

    assert result["error"] == (
        "Generated code violates the existing "
        "architecture."
    )

    assert (
        "Existing class 'Parser' was removed."
        in result["details"]
    )

    assert source.read_text(
        encoding="utf-8"
    ) == original


@pytest.mark.unit
def test_code_writer_repairs_removed_class(
    tmp_path,
):
    original = """\
class Parser:
    def parse(self, value):
        return value
"""

    generated = """\
class Other:
    def run(self):
        return 1
"""

    repaired = """\
class Parser:
    def parse(self, value):
        return value.strip()
"""

    source = tmp_path / "parser.py"
    source.write_text(
        original,
        encoding="utf-8",
    )

    class RepairTool:
        def __init__(self):
            self.calls = []

        def execute(self, request):
            self.calls.append(request)

            return {
                "success": True,
                "code": repaired,
            }

    repair_tool = RepairTool()

    writer = CodeWriterTool(
        llm=FakeLLM(
            response=generated
        ),
        workspace=tmp_path,
        registry=FakeRegistry(
            {
                "code_repair": repair_tool,
            }
        ),
    )

    result = writer.modify_file(
        "parser.py",
        ["Improve parser"],
    )

    assert result == {
        "file": "parser.py",
        "status": "updated",
    }

    assert len(repair_tool.calls) == 1

    assert (
        repair_tool.calls[0]["context"]
        == "Existing class 'Parser' was removed."
    )


@pytest.mark.unit
def test_code_writer_detects_removed_method(
    tmp_path,
):
    original = """\
class Parser:
    def parse(self, value):
        return value

    def validate(self, value):
        return True
"""

    generated = """\
class Parser:
    def parse(self, value):
        return value
"""

    source = tmp_path / "parser.py"
    source.write_text(
        original,
        encoding="utf-8",
    )

    writer = CodeWriterTool(
        llm=FakeLLM(
            response=generated
        ),
        workspace=tmp_path,
    )

    result = writer.modify_file(
        "parser.py",
        ["Change parser"],
    )

    assert result["error"] == (
        "Generated code violates the existing "
        "architecture."
    )

    assert (
        "lost existing methods"
        in result["details"]
    )

    assert "validate" in result["details"]


@pytest.mark.unit
def test_code_writer_detects_inheritance_change(
    tmp_path,
):
    original = """\
class Parser(BaseParser):
    def parse(self, value):
        return value
"""

    generated = """\
class Parser:
    def parse(self, value):
        return value.strip()
"""

    source = tmp_path / "parser.py"
    source.write_text(
        original,
        encoding="utf-8",
    )

    writer = CodeWriterTool(
        llm=FakeLLM(
            response=generated
        ),
        workspace=tmp_path,
    )

    result = writer.modify_file(
        "parser.py",
        ["Change parser"],
    )

    assert result["error"] == (
        "Generated code violates the existing "
        "architecture."
    )

    assert (
        "inheritance changed"
        in result["details"]
    )


@pytest.mark.unit
def test_code_writer_detects_removed_top_level_function(
    tmp_path,
):
    original = """\
def parse(value):
    return value


class Parser:
    def run(self):
        return True
"""

    generated = """\
class Parser:
    def run(self):
        return True
"""

    source = tmp_path / "parser.py"
    source.write_text(
        original,
        encoding="utf-8",
    )

    writer = CodeWriterTool(
        llm=FakeLLM(
            response=generated
        ),
        workspace=tmp_path,
    )

    result = writer.modify_file(
        "parser.py",
        ["Change parser"],
    )

    assert result["error"] == (
        "Generated code violates the existing "
        "architecture."
    )

    assert (
        "Existing top-level functions were removed"
        in result["details"]
    )

    assert "parse" in result["details"]


@pytest.mark.unit
def test_code_writer_repair_tool_exception_is_handled(
    tmp_path,
):
    original = """\
class Parser:
    def parse(self, value):
        return value
"""

    broken = """\
class Parser:
    def parse(self, value)
        return value
"""

    source = tmp_path / "parser.py"
    source.write_text(
        original,
        encoding="utf-8",
    )

    class ExplodingRepairTool:
        def execute(self, request):
            raise RuntimeError(
                "repair service unavailable"
            )

    writer = CodeWriterTool(
        llm=FakeLLM(
            response=broken
        ),
        workspace=tmp_path,
        registry=FakeRegistry(
            {
                "code_repair": ExplodingRepairTool(),
            }
        ),
    )

    result = writer.modify_file(
        "parser.py",
        ["Fix syntax"],
    )

    assert result["error"] == (
        "Generated code has invalid Python syntax "
        "and automatic repair failed."
    )

    assert source.read_text(
        encoding="utf-8"
    ) == original


@pytest.mark.unit
def test_code_writer_repair_tool_missing_returns_failure(
    tmp_path,
):
    original = """\
class Parser:
    def parse(self, value):
        return value
"""

    generated = """\
class Other:
    def run(self):
        return True
"""

    source = tmp_path / "parser.py"
    source.write_text(
        original,
        encoding="utf-8",
    )

    writer = CodeWriterTool(
        llm=FakeLLM(
            response=generated
        ),
        workspace=tmp_path,
        registry=FakeRegistry(),
    )

    result = writer.modify_file(
        "parser.py",
        ["Replace parser"],
    )

    assert result["error"] == (
        "Generated code violates the existing "
        "architecture."
    )

    assert (
        "Existing class 'Parser' was removed."
        in result["details"]
    )

    assert source.read_text(
        encoding="utf-8"
    ) == original


@pytest.mark.unit
def test_code_writer_repair_returns_invalid_code(
    tmp_path,
):
    original = """\
class Parser:
    def parse(self, value):
        return value
"""

    generated = """\
class Other:
    def run(self):
        return True
"""

    source = tmp_path / "parser.py"
    source.write_text(
        original,
        encoding="utf-8",
    )

    class InvalidRepairTool:
        def execute(self, request):
            return {
                "success": True,
                "code": "",
            }

    writer = CodeWriterTool(
        llm=FakeLLM(
            response=generated
        ),
        workspace=tmp_path,
        registry=FakeRegistry(
            {
                "code_repair": InvalidRepairTool(),
            }
        ),
    )

    result = writer.modify_file(
        "parser.py",
        ["Replace parser"],
    )

    assert result["error"] == (
        "Generated code violates the existing "
        "architecture."
    )

    assert source.read_text(
        encoding="utf-8"
    ) == original

@pytest.mark.unit
def test_code_writer_blocks_path_outside_workspace(
    tmp_path,
):
    source = tmp_path / "parser.py"
    source.write_text(
        "class Parser:\n    pass\n",
        encoding="utf-8",
    )

    writer = CodeWriterTool(
        llm=FakeLLM(),
        workspace=tmp_path,
    )

    result = writer.modify_file(
        "../parser.py",
        ["Modify parser"],
    )

    assert result == {
        "file": "../parser.py",
        "error": "Path is outside the workspace.",
    }


@pytest.mark.unit
def test_code_writer_returns_failure_for_missing_file(
    tmp_path,
):
    writer = CodeWriterTool(
        llm=FakeLLM(),
        workspace=tmp_path,
    )

    result = writer.modify_file(
        "missing.py",
        ["Create parser"],
    )

    assert result == {
        "file": "missing.py",
        "error": "File not found.",
    }


@pytest.mark.unit
def test_code_writer_rejects_directory_target(
    tmp_path,
):
    directory = tmp_path / "parser.py"
    directory.mkdir()

    writer = CodeWriterTool(
        llm=FakeLLM(),
        workspace=tmp_path,
    )

    result = writer.modify_file(
        "parser.py",
        ["Modify parser"],
    )

    assert result == {
        "file": "parser.py",
        "error": "Target is not a file.",
    }


@pytest.mark.unit
def test_code_writer_handles_llm_exception(
    tmp_path,
):
    source = tmp_path / "parser.py"

    original = """\
class Parser:
    pass
"""

    source.write_text(
        original,
        encoding="utf-8",
    )

    class ExplodingLLM:
        def generate(self, prompt):
            raise RuntimeError(
                "LLM unavailable"
            )

    writer = CodeWriterTool(
        llm=ExplodingLLM(),
        workspace=tmp_path,
    )

    result = writer.modify_file(
        "parser.py",
        ["Modify parser"],
    )

    assert result == {
        "file": "parser.py",
        "error": (
            "Code generation failed: "
            "LLM unavailable"
        ),
    }

    assert source.read_text(
        encoding="utf-8"
    ) == original


@pytest.mark.unit
def test_code_writer_handles_invalid_llm_response_dict(
    tmp_path,
):
    source = tmp_path / "parser.py"

    original = """\
class Parser:
    pass
"""

    source.write_text(
        original,
        encoding="utf-8",
    )

    writer = CodeWriterTool(
        llm=FakeLLM(
            response={
                "success": False,
                "error": "generation failed",
            }
        ),
        workspace=tmp_path,
    )

    result = writer.modify_file(
        "parser.py",
        ["Modify parser"],
    )

    assert result == {
        "file": "parser.py",
        "error": {
            "success": False,
            "error": "generation failed",
        },
    }

    assert source.read_text(
        encoding="utf-8"
    ) == original


@pytest.mark.unit
def test_code_writer_handles_invalid_llm_response_type(
    tmp_path,
):
    source = tmp_path / "parser.py"

    source.write_text(
        "class Parser:\n    pass\n",
        encoding="utf-8",
    )

    writer = CodeWriterTool(
        llm=FakeLLM(
            response=12345
        ),
        workspace=tmp_path,
    )

    result = writer.modify_file(
        "parser.py",
        ["Modify parser"],
    )

    assert result == {
        "file": "parser.py",
        "error": (
            "LLM returned an invalid response type."
        ),
    }


@pytest.mark.unit
def test_code_writer_rejects_empty_llm_code(
    tmp_path,
):
    source = tmp_path / "parser.py"

    original = """\
class Parser:
    pass
"""

    source.write_text(
        original,
        encoding="utf-8",
    )

    writer = CodeWriterTool(
        llm=FakeLLM(
            response="   "
        ),
        workspace=tmp_path,
    )

    result = writer.modify_file(
        "parser.py",
        ["Modify parser"],
    )

    assert result == {
        "file": "parser.py",
        "error": "LLM returned empty code.",
    }

    assert source.read_text(
        encoding="utf-8"
    ) == original


@pytest.mark.unit
def test_code_writer_execute_reports_partial_failure(
    tmp_path,
):
    source_a = tmp_path / "a.py"
    source_b = tmp_path / "b.py"

    source_a.write_text(
        "class A:\n    pass\n",
        encoding="utf-8",
    )

    source_b.write_text(
        "class B:\n    pass\n",
        encoding="utf-8",
    )

    class SequentialLLM:
        def __init__(self):
            self.responses = [
                "class A:\n    pass\n",
                "class Other:\n    pass\n",
            ]

        def generate(self, prompt):
            return self.responses.pop(0)

    writer = CodeWriterTool(
        llm=SequentialLLM(),
        workspace=tmp_path,
    )

    result = writer.execute(
        {
            "files": [
                {
                    "path": "a.py",
                    "changes": ["Update A"],
                },
                {
                    "path": "b.py",
                    "changes": ["Update B"],
                },
            ],
        }
    )

    assert result["success"] is False

    assert len(result["results"]) == 2

    assert result["results"][0] == {
        "file": "a.py",
        "status": "updated",
    }

    assert result["results"][1]["file"] == "b.py"
    assert "error" in result["results"][1]


@pytest.mark.unit
def test_code_writer_execute_rejects_invalid_plan():
    writer = CodeWriterTool(
        llm=FakeLLM(),
    )

    assert writer.execute(
        None
    ) == {
        "success": False,
        "message": "Invalid plan.",
    }


@pytest.mark.unit
def test_code_writer_execute_rejects_invalid_files_list():
    writer = CodeWriterTool(
        llm=FakeLLM(),
    )

    assert writer.execute(
        {
            "files": "parser.py",
        }
    ) == {
        "success": False,
        "message": "Invalid files list.",
    }


@pytest.mark.unit
def test_code_writer_execute_handles_no_valid_files():
    writer = CodeWriterTool(
        llm=FakeLLM(),
    )

    result = writer.execute(
        {
            "files": [
                {},
                {
                    "path": "",
                    "changes": [],
                },
                "invalid",
            ],
        }
    )

    assert result == {
        "success": False,
        "message": "No valid files were provided.",
        "results": [],
    }

@pytest.mark.unit
def test_code_writer_returns_written_files(tmp_path):
    writer = CodeWriterTool(
        llm=None,
        workspace=tmp_path,
    )

    writer.modify_file = lambda filename, changes: {
        "file": filename,
        "status": "updated",
    }

    result = writer.execute({
        "files": [
            {
                "path": "app/parser.py",
                "changes": [
                    "Fix parser"
                ],
            },
            {
                "path": "app/tokenizer.py",
                "changes": [
                    "Fix tokenizer"
                ],
            },
        ]
    })

    assert result["success"] is True

    assert result["files_written"] == [
        "app/parser.py",
        "app/tokenizer.py",
    ]

@pytest.mark.unit
def test_code_writer_excludes_failed_files_from_files_written(tmp_path):
    writer = CodeWriterTool(
        llm=None,
        workspace=tmp_path,
    )

    def fake_modify_file(filename, changes):
        if filename == "app/parser.py":
            return {
                "file": filename,
                "status": "updated",
            }

        return {
            "file": filename,
            "error": "Write failed.",
        }

    writer.modify_file = fake_modify_file

    result = writer.execute({
        "files": [
            {
                "path": "app/parser.py",
                "changes": [
                    "Fix parser"
                ],
            },
            {
                "path": "app/tokenizer.py",
                "changes": [
                    "Fix tokenizer"
                ],
            },
        ]
    })

    assert result["success"] is False

    assert result["files_written"] == [
        "app/parser.py",
    ]

@pytest.mark.unit
def test_code_writer_detects_removed_import(
    tmp_path,
):
    original = """\
import os

class Parser:
    def parse(self, value):
        return value
"""

    generated = """\
class Parser:
    def parse(self, value):
        return value.strip()
"""

    source = tmp_path / "parser.py"

    source.write_text(
        original,
        encoding="utf-8",
    )

    writer = CodeWriterTool(
        llm=FakeLLM(
            response=generated
        ),
        workspace=tmp_path,
    )

    result = writer.modify_file(
        "parser.py",
        ["Change parser"],
    )

    assert result["error"] == (
        "Generated code violates the existing "
        "architecture."
    )

    assert (
        "Existing imports were removed"
        in result["details"]
    )

    assert "import os" in result["details"]

    assert source.read_text(
        encoding="utf-8"
    ) == original