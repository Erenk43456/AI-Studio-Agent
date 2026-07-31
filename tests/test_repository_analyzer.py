"""Tests for the structured repository analysis (data/format separation)."""

import json

from tools.repository_analysis import RepositoryAnalysis
from tools.repository_report import RepositoryReportFormatter
from tools.repository_analyzer import RepositoryAnalyzerTool

# ----------------------------------------------------------------------
# RepositoryAnalysis data model
# ----------------------------------------------------------------------


def test_analysis_defaults_are_empty_containers():
    analysis = RepositoryAnalysis(generated_at="2026-01-01 00:00:00")
    assert analysis.overview == {}
    assert analysis.module_roles == {}
    assert analysis.definitions == {}
    assert analysis.tools == []
    assert analysis.registry_names == []
    assert analysis.wiring_checks == []
    assert analysis.issues == []


def test_analysis_to_dict_round_trip():
    analysis = RepositoryAnalysis(
        generated_at="2026-01-01 00:00:00",
        overview={"python_files": 3},
        wiring_checks=[{"label": "x", "ok": True}],
    )
    data = analysis.to_dict()
    assert data["generated_at"] == "2026-01-01 00:00:00"
    assert data["overview"] == {"python_files": 3}
    assert data["wiring_checks"] == [{"label": "x", "ok": True}]
    # to_dict is a plain dict -> JSON serializable (future agent input)
    json.dumps(data)


# ----------------------------------------------------------------------
# RepositoryReportFormatter rendering
# ----------------------------------------------------------------------


def test_formatter_renders_all_sections():
    analysis = RepositoryAnalysis(
        generated_at="2026-01-01 00:00:00",
        overview={
            "root": "C:/repo",
            "python_files": 2,
            "total_lines": 40,
            "top_level_modules": ["app", "tools"],
            "largest_files": [
                {"file": "app/main.py", "lines": 30},
                {"file": "tools/x.py", "lines": 10},
            ],
        },
        module_roles={"app/core/container.py": "DI root"},
        definitions={"app/core/container.py": ["class AIContainer("]},
        tools=[
            {"file": "calculator.py", "has_execute": True},
            {"file": "broken.py", "has_execute": False},
        ],
        registry_names=["calculator", "repository_analyzer"],
        wiring_checks=[
            {"label": "Check A", "ok": True},
            {"label": "Check B", "ok": False},
        ],
        issues=[
            {"file": "app/x.py", "line": 3, "message": "# TODO fix"},
            {"file": "app/y.py", "line": 7, "message": "# FIXME later"},
        ],
    )

    report = RepositoryReportFormatter.render(analysis)

    assert "AI-Studio-Agent Repository Analysis" in report
    assert "[1] Overview" in report
    assert "- Python files: 2" in report
    assert "- Total lines: 40" in report
    assert "- Top-level modules: app, tools" in report
    assert "app/main.py (30 lines)" in report
    assert "[2] Module Roles (architecture)" in report
    assert "app/core/container.py" in report
    assert "-> DI root" in report
    assert "[3] Key Definitions" in report
    assert "class AIContainer(" in report
    assert "[4] Tool Registry" in report
    assert "calculator.py: execute(): OK" in report
    assert "broken.py: execute(): MISSING" in report
    assert "Registered names in AIContainer: calculator, repository_analyzer" in report
    assert "[5] Architecture & Wiring Checks" in report
    assert "- [OK] Check A" in report
    assert "- [FAIL] Check B" in report
    assert "[6] TODO / FIXME Markers" in report
    assert "app/x.py:3: # TODO fix" in report


def test_formatter_empty_analysis():
    analysis = RepositoryAnalysis(generated_at="2026-01-01 00:00:00")
    report = RepositoryReportFormatter.render(analysis)
    assert "tools/ directory not found." in report
    assert "- No TODO/FIXME markers found." in report


def test_formatter_does_not_mutate_data():
    analysis = RepositoryAnalysis(
        generated_at="2026-01-01 00:00:00",
        overview={
            "root": "C:/repo",
            "python_files": 2,
            "total_lines": 40,
            "top_level_modules": ["app"],
            "largest_files": [{"file": "a.py", "lines": 5}],
        },
        issues=[{"file": "a.py", "line": 1, "message": "# TODO"}],
    )
    overview = dict(analysis.overview)
    issues = list(analysis.issues)
    RepositoryReportFormatter.render(analysis)
    assert analysis.overview == overview
    assert analysis.issues == issues


# ----------------------------------------------------------------------
# Analyzer behavior (data layer + marker correctness)
# ----------------------------------------------------------------------


def test_analyzer_returns_structured_analysis(tmp_path):
    proj = tmp_path / "repo"
    proj.mkdir()
    (proj / "main.py").write_text("print('hi')\n", encoding="utf-8")
    (proj / "app" / "core").mkdir(
        parents=True
    )
    (proj / "app" / "core" / "container.py").write_text(
        "# TODO register more tools\n"
        'registry.register("calculator", Calculator())\n'
        'registry.register("repository_analyzer", RepositoryAnalyzerTool())\n',
        encoding="utf-8",
    )
    (proj / "tools").mkdir()
    (proj / "tools" / "calculator.py").write_text(
        "class Calculator:\n    def execute(self, plan):\n        return 1\n",
        encoding="utf-8",
    )
    (proj / "tools" / "repository_analysis.py").write_text(
        "from dataclasses import dataclass\n@dataclass\nclass RepositoryAnalysis:\n    pass\n",
        encoding="utf-8",
    )
    (proj / "tools" / "repository_report.py").write_text(
        "class RepositoryReportFormatter:\n    pass\n",
        encoding="utf-8",
    )

    tool = RepositoryAnalyzerTool(str(proj))
    result = tool.analyze(proj)

    assert isinstance(result, RepositoryAnalysis)
    assert result.overview["python_files"] == 5
    assert result.overview["top_level_modules"] == ["app", "tools"]
    assert "repository_analyzer" in result.registry_names
    assert "calculator" in result.registry_names
    # tools list excludes the new data/formatter modules.
    tool_files = {item["file"] for item in result.tools}
    assert "calculator.py" in tool_files
    assert "repository_analysis.py" not in tool_files
    assert "repository_report.py" not in tool_files
    # Only real comments match markers: the container.py comment is real,
    # the string literals in the probe tools files must not match.
    assert {
        "file": "app/core/container.py",
        "line": 1,
        "message": "# TODO register more tools",
    } in result.issues


def test_marker_scan_ignores_strings_and_analyzer_itself(tmp_path):
    proj = tmp_path / "repo"
    proj.mkdir()
    (proj / "main.py").write_text("print('hi')\n", encoding="utf-8")
    (proj / "tools").mkdir()
    (proj / "tools" / "probe.py").write_text(
        's = "TODO not a comment"\n'
        "r = '# FIXME also a string'\n"
        "# XXX real comment\n",
        encoding="utf-8",
    )
    # Simulates the analyzer's own implementation being scanned.
    (proj / "tools" / "repository_analyzer.py").write_text(
        'import re\nP = re.compile(r"TODO|FIXME|XXX")\n'
        "# TODO real comment but file must be excluded\n",
        encoding="utf-8",
    )

    tool = RepositoryAnalyzerTool(str(proj))
    issues = tool._collect_issues(proj)

    messages = [issue["message"] for issue in issues]
    assert messages == ["# XXX real comment"]
    # Analyzer implementation file excluded even though it has a real TODO.
    files = [issue["file"] for issue in issues]
    assert "tools/repository_analyzer.py" not in files
    # The regex literal with markers was not reported (comment-only scan).
    assert not any("re.compile" in m for m in messages)


# ----------------------------------------------------------------------
# Public tool contract (ToolRegistry compatibility)
# ----------------------------------------------------------------------


def test_execute_returns_text_report(tmp_path):
    proj = tmp_path / "repo"
    proj.mkdir()
    (proj / "main.py").write_text("print('hi')\n", encoding="utf-8")

    tool = RepositoryAnalyzerTool(str(proj))
    report = tool.execute({"action": "analyze"})
    assert isinstance(report, str)
    assert "AI-Studio-Agent Repository Analysis" in report
    assert "repository_analyzer registered in container" in report


def test_execute_invalid_action(tmp_path):
    proj = tmp_path / "repo"
    proj.mkdir()
    (proj / "main.py").write_text("print('hi')\n", encoding="utf-8")

    tool = RepositoryAnalyzerTool(str(proj))
    assert tool.execute({"action": "review"}) == "Unsupported repository action."
