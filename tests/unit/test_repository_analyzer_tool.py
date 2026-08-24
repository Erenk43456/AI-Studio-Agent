import pytest

from tools.repository_analyzer import RepositoryAnalyzerTool
from tools.code_analyzer_tool import CodeAnalyzerTool


@pytest.mark.unit
def test_repository_analyzer_has_expected_tool_metadata():
    analyzer = RepositoryAnalyzerTool()

    assert analyzer.name == "repository_analyzer"
    assert analyzer.safe is True
    assert analyzer.modifies_files is False
    assert analyzer.requires_confirmation is False


@pytest.mark.unit
def test_repository_analyzer_analyze_returns_path_not_found(
    tmp_path,
):
    missing = tmp_path / "missing"

    analyzer = RepositoryAnalyzerTool()

    result = analyzer.analyze(missing)

    assert result == (f"Path not found: {missing}")


@pytest.mark.unit
def test_repository_analyzer_analyze_rejects_non_repository_root(
    tmp_path,
):
    analyzer = RepositoryAnalyzerTool()

    result = analyzer.analyze(tmp_path)

    assert result == (f"Not an AI-Studio-Agent repository root: " f"{tmp_path}")


@pytest.mark.unit
def test_repository_analyzer_iter_python_files_skips_ignored_directories(
    tmp_path,
):
    (tmp_path / "main.py").write_text(
        "print('main')",
        encoding="utf-8",
    )

    (tmp_path / "valid.py").write_text(
        "print('valid')",
        encoding="utf-8",
    )

    ignored = tmp_path / "venv"
    ignored.mkdir()

    (ignored / "ignored.py").write_text(
        "print('ignored')",
        encoding="utf-8",
    )

    cache = tmp_path / "__pycache__"
    cache.mkdir()

    (cache / "cache.py").write_text(
        "print('cache')",
        encoding="utf-8",
    )

    analyzer = RepositoryAnalyzerTool()

    files = list(analyzer._iter_python_files(tmp_path))

    names = {path.name for path in files}

    assert names == {
        "main.py",
        "valid.py",
    }


@pytest.mark.unit
def test_repository_analyzer_iter_python_files_skips_init_files(
    tmp_path,
):
    (tmp_path / "main.py").write_text(
        "print('main')",
        encoding="utf-8",
    )

    (tmp_path / "__init__.py").write_text(
        "",
        encoding="utf-8",
    )

    files = list(RepositoryAnalyzerTool()._iter_python_files(tmp_path))

    assert all(path.name != "__init__.py" for path in files)


@pytest.mark.unit
def test_repository_analyzer_read_uses_utf8_and_replaces_invalid_bytes(
    tmp_path,
):
    source = tmp_path / "broken.py"

    source.write_bytes(b"print('hello')\xff")

    result = RepositoryAnalyzerTool._read(source)

    assert result.startswith("print('hello')")

    assert "\ufffd" in result


@pytest.mark.unit
def test_repository_analyzer_top_level_defs_collects_functions_and_classes():
    source = """\
import os

CONSTANT = 1

def parse(value):
    return value

class Parser:
    def run(self):
        pass

if True:
    def nested():
        pass
"""

    result = RepositoryAnalyzerTool._top_level_defs(source)

    assert result == [
        "def parse(",
        "class Parser(run)",
    ]


@pytest.mark.unit
def test_repository_analyzer_top_level_defs_returns_empty_for_invalid_python():
    result = RepositoryAnalyzerTool._top_level_defs("def broken(:\n")

    assert result == []


@pytest.mark.unit
def test_repository_analyzer_analyze_accepts_repository_with_main_py(
    tmp_path,
):
    (tmp_path / "main.py").write_text(
        "print('main')",
        encoding="utf-8",
    )

    analyzer = RepositoryAnalyzerTool()

    result = analyzer.analyze(tmp_path)

    assert not isinstance(
        result,
        str,
    )

    assert hasattr(
        result,
        "generated_at",
    )

    assert hasattr(
        result,
        "overview",
    )

    assert hasattr(
        result,
        "definitions",
    )

    assert hasattr(
        result,
        "tools",
    )

    assert hasattr(
        result,
        "issues",
    )

    assert result.repository_root == str(tmp_path.resolve())
    assert "python" in result.languages
    assert "main.py" in result.files


@pytest.mark.unit
def test_repository_analyzer_execute_defaults_to_analyze(
    tmp_path,
):
    (tmp_path / "main.py").write_text(
        "print('main')",
        encoding="utf-8",
    )

    analyzer = RepositoryAnalyzerTool(root=tmp_path)

    result = analyzer.execute({})

    assert isinstance(
        result,
        str,
    )

    assert "Repository" in result or "repository" in result


@pytest.mark.unit
def test_repository_analyzer_accepts_non_python_repository_marker(
    tmp_path,
):
    (tmp_path / "README.md").write_text(
        "A repository",
        encoding="utf-8",
    )
    (tmp_path / "index.ts").write_text(
        "export const value = 1;",
        encoding="utf-8",
    )

    result = RepositoryAnalyzerTool().analyze(tmp_path)

    assert not isinstance(result, str)
    assert result.languages == {
        "markdown": 1,
        "typescript": 1,
    }
    assert result.test_files == []


@pytest.mark.unit
def test_repository_analyzer_execute_rejects_unsupported_action():
    analyzer = RepositoryAnalyzerTool()

    result = analyzer.execute(
        {
            "action": "repair",
        }
    )

    assert result == ("Unsupported repository action.")


@pytest.mark.unit
def test_repository_analyzer_collect_definitions_reads_python_files(
    tmp_path,
):
    (tmp_path / "main.py").write_text(
        """\
def main():
    return True


class Application:
    def run(self):
        pass
""",
        encoding="utf-8",
    )

    analyzer = RepositoryAnalyzerTool()

    result = analyzer._collect_definitions(tmp_path)

    assert isinstance(result, dict)


@pytest.mark.unit
def test_repository_analyzer_collect_definitions_skips_invalid_python(
    tmp_path,
):
    (tmp_path / "main.py").write_text(
        "def main():\n    return True\n",
        encoding="utf-8",
    )

    (tmp_path / "broken.py").write_text(
        "def broken(:\n",
        encoding="utf-8",
    )

    analyzer = RepositoryAnalyzerTool()

    result = analyzer._collect_definitions(tmp_path)

    assert isinstance(result, dict)


@pytest.mark.unit
def test_repository_analyzer_collect_module_roles_uses_known_roles(
    tmp_path,
):
    known = tmp_path / "app" / "core" / "containers"

    known.mkdir(parents=True)

    target = known / "main_container.py"

    target.write_text(
        "class MainContainer:\n    pass\n",
        encoding="utf-8",
    )

    analyzer = RepositoryAnalyzerTool()

    result = analyzer._collect_module_roles(tmp_path)

    assert isinstance(result, dict)

    relative = "app/core/containers/" "main_container.py"

    assert relative in result
    assert result[relative] == ("Application dependency injection " "composition root")


@pytest.mark.unit
def test_repository_analyzer_collect_module_roles_ignores_missing_known_files(
    tmp_path,
):
    analyzer = RepositoryAnalyzerTool()

    result = analyzer._collect_module_roles(tmp_path)

    assert result == {}


@pytest.mark.unit
def test_repository_analyzer_collect_overview_reports_python_files(
    tmp_path,
):
    (tmp_path / "main.py").write_text(
        "print('main')\n",
        encoding="utf-8",
    )

    (tmp_path / "parser.py").write_text(
        "class Parser:\n    pass\n",
        encoding="utf-8",
    )

    analyzer = RepositoryAnalyzerTool()

    result = analyzer._collect_overview(tmp_path)

    assert isinstance(result, dict)

    # The overview must contain information
    # about the discovered Python files.
    assert result


@pytest.mark.unit
def test_repository_analyzer_collect_tools_discovers_tool_files(
    tmp_path,
):
    tools_dir = tmp_path / "tools"

    tools_dir.mkdir()

    (tools_dir / "calculator_tool.py").write_text(
        """\
class CalculatorTool:
    name = "calculator"
""",
        encoding="utf-8",
    )

    (tools_dir / "file_tool.py").write_text(
        """\
class FileTool:
    name = "file"
""",
        encoding="utf-8",
    )

    analyzer = RepositoryAnalyzerTool()

    tools, registry_names = analyzer._collect_tools(tmp_path)

    assert isinstance(tools, list)
    assert isinstance(
        registry_names,
        list,
    )

    tool_files = {item["file"] for item in tools}

    assert "calculator_tool.py" in tool_files

    assert "file_tool.py" in tool_files


@pytest.mark.unit
def test_repository_analyzer_collect_tools_excludes_tool_infrastructure_files(
    tmp_path,
):
    tools_dir = tmp_path / "tools"

    tools_dir.mkdir()

    for filename in (
        "base_tool.py",
        "tool_registry.py",
        "repository_analysis.py",
        "repository_report.py",
        "__init__.py",
    ):
        (tools_dir / filename).write_text(
            "class Dummy:\n    pass\n",
            encoding="utf-8",
        )

    (tools_dir / "calculator_tool.py").write_text(
        """\
class CalculatorTool:
    name = "calculator"
""",
        encoding="utf-8",
    )

    analyzer = RepositoryAnalyzerTool()

    tools, _ = analyzer._collect_tools(tmp_path)

    tool_files = {item["file"] for item in tools}

    assert tool_files == {"calculator_tool.py"}


@pytest.mark.unit
def test_repository_analyzer_collect_wiring_checks_returns_check_results(
    tmp_path,
):
    main_container = tmp_path / "app" / "core" / "containers"

    main_container.mkdir(parents=True)

    (main_container / "main_container.py").write_text(
        "self.core = CoreContainer(\n",
        encoding="utf-8",
    )

    analyzer = RepositoryAnalyzerTool()

    result = analyzer._collect_wiring_checks(tmp_path)

    assert isinstance(result, list)


@pytest.mark.unit
def test_repository_analyzer_collect_issues_returns_list(
    tmp_path,
):
    (tmp_path / "main.py").write_text(
        """\
# TODO: implement startup
def main():
    pass
""",
        encoding="utf-8",
    )

    analyzer = RepositoryAnalyzerTool()

    result = analyzer._collect_issues(tmp_path)

    assert isinstance(result, list)


@pytest.mark.unit
def test_code_analyzer_analysis_status_passes_clean_analysis():
    analysis = {
        "summary": "Looks good",
        "syntax_errors": [],
        "logical_errors": [],
        "security_issues": [],
        "performance_issues": [],
        "architecture_issues": [],
        "improvements": [],
        "risk_level": "low",
    }

    assert CodeAnalyzerTool.get_analysis_status(analysis) == "pass"


@pytest.mark.unit
def test_code_analyzer_analysis_status_passes_performance_issue():
    analysis = {
        "summary": "Minor optimization possible",
        "syntax_errors": [],
        "logical_errors": [],
        "security_issues": [],
        "performance_issues": ["This loop could be optimized."],
        "architecture_issues": [],
        "improvements": [],
        "risk_level": "low",
    }

    assert CodeAnalyzerTool.get_analysis_status(analysis) == "pass"


@pytest.mark.unit
def test_code_analyzer_analysis_status_fails_syntax_error():
    analysis = {
        "summary": "Syntax problem",
        "syntax_errors": ["Missing closing parenthesis."],
        "logical_errors": [],
        "security_issues": [],
        "performance_issues": [],
        "architecture_issues": [],
        "improvements": [],
        "risk_level": "low",
    }

    assert CodeAnalyzerTool.get_analysis_status(analysis) == "fail"


@pytest.mark.unit
def test_code_analyzer_analysis_status_fails_logical_error():
    analysis = {
        "summary": "Logical problem",
        "syntax_errors": [],
        "logical_errors": ["Function returns the wrong value."],
        "security_issues": [],
        "performance_issues": [],
        "architecture_issues": [],
        "improvements": [],
        "risk_level": "low",
    }

    assert CodeAnalyzerTool.get_analysis_status(analysis) == "fail"


@pytest.mark.unit
def test_code_analyzer_analysis_status_fails_security_issue():
    analysis = {
        "summary": "Security problem",
        "syntax_errors": [],
        "logical_errors": [],
        "security_issues": ["Unsafe subprocess usage."],
        "performance_issues": [],
        "architecture_issues": [],
        "improvements": [],
        "risk_level": "low",
    }

    assert CodeAnalyzerTool.get_analysis_status(analysis) == "fail"


@pytest.mark.unit
def test_code_analyzer_analysis_status_fails_architecture_issue():
    analysis = {
        "summary": "Architecture problem",
        "syntax_errors": [],
        "logical_errors": [],
        "security_issues": [],
        "performance_issues": [],
        "architecture_issues": ["Public API was changed."],
        "improvements": [],
        "risk_level": "low",
    }

    assert CodeAnalyzerTool.get_analysis_status(analysis) == "fail"


@pytest.mark.unit
def test_code_analyzer_analysis_status_fails_high_risk_analysis():
    analysis = {
        "summary": "High risk",
        "syntax_errors": [],
        "logical_errors": [],
        "security_issues": [],
        "performance_issues": [],
        "architecture_issues": [],
        "improvements": [],
        "risk_level": "high",
    }

    assert CodeAnalyzerTool.get_analysis_status(analysis) == "fail"


@pytest.mark.unit
def test_code_analyzer_analysis_status_fails_critical_risk_analysis():
    analysis = {
        "summary": "Critical risk",
        "syntax_errors": [],
        "logical_errors": [],
        "security_issues": [],
        "performance_issues": [],
        "architecture_issues": [],
        "improvements": [],
        "risk_level": "critical",
    }

    assert CodeAnalyzerTool.get_analysis_status(analysis) == "fail"


@pytest.mark.unit
def test_code_analyzer_analysis_status_fails_parse_error():
    analysis = {
        "raw_response": '{"broken":}',
        "parse_error": True,
    }

    assert CodeAnalyzerTool.get_analysis_status(analysis) == "fail"


@pytest.mark.unit
def test_code_analyzer_analysis_status_fails_invalid_analysis_type():
    assert CodeAnalyzerTool.get_analysis_status(None) == "fail"

    assert CodeAnalyzerTool.get_analysis_status("invalid") == "fail"
