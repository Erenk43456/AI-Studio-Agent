import pytest

import tools.code_writer_tool as module

from tools.code_writer_tool import CodeWriterTool


class FakeLLM:

    def generate(self, prompt):
        return (
            "class Example:\n"
            "    value = 42\n"
        )


class FakeAtomicWriter:

    instances = []

    def __init__(self, workspace):
        self.workspace = workspace
        self.calls = []

        FakeAtomicWriter.instances.append(
            self
        )

    def write(
        self,
        path,
        content
    ):

        self.calls.append(
            {
                "path": path,
                "content": content
            }
        )

        return {
            "success": True,
            "path": str(path)
        }


@pytest.mark.unit
def test_code_writer_uses_atomic_writer(
    tmp_path,
    monkeypatch
):

    FakeAtomicWriter.instances.clear()

    monkeypatch.setattr(
        module,
        "AtomicWriter",
        FakeAtomicWriter
    )

    source = tmp_path / "example.py"

    source.write_text(
        "class Example:\n"
        "    value = 1\n",
        encoding="utf-8"
    )

    writer = CodeWriterTool(
        llm=FakeLLM(),
        workspace=tmp_path
    )

    result = writer.modify_file(
        "example.py",
        [
            "Change value to 42."
        ]
    )

    assert result["status"] == "updated"

    assert len(
        FakeAtomicWriter.instances
    ) == 1

    atomic_writer = (
        FakeAtomicWriter.instances[0]
    )

    assert len(
        atomic_writer.calls
    ) == 1

    assert (
        atomic_writer.calls[0]["content"]
        ==
        "class Example:\n"
        "    value = 42\n"
    )


@pytest.mark.unit
def test_code_writer_does_not_directly_write_file(
    tmp_path,
    monkeypatch
):

    monkeypatch.setattr(
        module,
        "AtomicWriter",
        FakeAtomicWriter
    )

    source = tmp_path / "example.py"

    original = (
        "class Example:\n"
        "    value = 1\n"
    )

    source.write_text(
        original,
        encoding="utf-8"
    )

    writer = CodeWriterTool(
        llm=FakeLLM(),
        workspace=tmp_path
    )

    writer.modify_file(
        "example.py",
        [
            "Change value to 42."
        ]
    )

    # FakeAtomicWriter does not actually write.
    # Therefore the original file must remain untouched.
    assert source.read_text(
        encoding="utf-8"
    ) == original