import pytest

from tools.python_analyzer import PythonAnalyzer


@pytest.mark.unit
def test_python_analyzer_collects_symbols_and_imports(tmp_path):
    source = tmp_path / "module.py"
    source.write_text(
        "import os\n\ndef parse(value):\n    return value\n\nclass Parser:\n    def run(self):\n        pass\n",
        encoding="utf-8",
    )

    result = PythonAnalyzer().analyze_file(source, tmp_path)

    assert result["definitions"] == ["def parse(", "class Parser(run)"]
    assert {item["kind"] for item in result["symbols"]} == {
        "function",
        "class",
        "method",
    }
    assert result["dependencies"][0]["target"] == "os"


@pytest.mark.unit
def test_python_analyzer_skips_invalid_python(tmp_path):
    source = tmp_path / "broken.py"
    source.write_text("def broken(:\n", encoding="utf-8")

    assert PythonAnalyzer().analyze_file(source, tmp_path) == {
        "symbols": [],
        "dependencies": [],
        "definitions": [],
    }
