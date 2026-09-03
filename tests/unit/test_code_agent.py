import pytest

from agents.code_agent import CodeAgent

from tests.fakes.fake_development_context import FakeDevelopmentContext
from tests.fakes.fake_llm import FakeLLM
from tests.fakes.fake_registry import FakeRegistry
from tests.fakes.fake_tool import FakeTool


@pytest.mark.unit
def test_code_agent_execute_uses_input_as_task(monkeypatch):
    agent = CodeAgent(
        FakeLLM(),
        FakeRegistry(),
    )

    calls = []

    def fake_run(task, development_context=None):
        calls.append(
            {
                "task": task,
                "development_context": development_context,
            }
        )

        return {
            "success": True
        }

    monkeypatch.setattr(
        agent,
        "run",
        fake_run,
    )

    result = agent.execute(
        {
            "input": "Fix the authentication bug",
            "message": "Ignored message",
            "task": "Ignored task",
        }
    )

    assert result == {
        "success": True
    }

    assert calls == [
        {
            "task": "Fix the authentication bug",
            "development_context": None,
        }
    ]


@pytest.mark.unit
def test_code_agent_execute_uses_message_when_input_missing(monkeypatch):
    agent = CodeAgent(
        FakeLLM(),
        FakeRegistry(),
    )

    calls = []

    monkeypatch.setattr(
        agent,
        "run",
        lambda task, development_context=None: calls.append(task)
        or {"success": True},
    )

    agent.execute(
        {
            "message": "Implement login validation",
            "task": "Fallback task",
        }
    )

    assert calls == [
        "Implement login validation"
    ]


@pytest.mark.unit
def test_code_agent_execute_uses_task_when_input_and_message_missing(
    monkeypatch,
):
    agent = CodeAgent(
        FakeLLM(),
        FakeRegistry(),
    )

    calls = []

    monkeypatch.setattr(
        agent,
        "run",
        lambda task, development_context=None: calls.append(task)
        or {"success": True},
    )

    agent.execute(
        {
            "task": "Refactor the parser",
        }
    )

    assert calls == [
        "Refactor the parser"
    ]


@pytest.mark.unit
def test_code_agent_execute_accepts_plain_string(monkeypatch):
    agent = CodeAgent(
        FakeLLM(),
        FakeRegistry(),
    )

    calls = []

    monkeypatch.setattr(
        agent,
        "run",
        lambda task, development_context=None: calls.append(task)
        or {"success": True},
    )

    agent.execute(
        "Add a unit test for the parser"
    )

    assert calls == [
        "Add a unit test for the parser"
    ]


@pytest.mark.unit
def test_code_agent_run_successfully_calls_code_writer():
    llm = FakeLLM(
        response="""
        {
            "summary": "Implement parser validation",
            "files": [
                {
                    "path": "app/parser.py",
                    "purpose": "Add validation",
                    "changes": [
                        "Validate parser input"
                    ]
                }
            ],
            "implementation": [
                "Add parser validation"
            ],
            "risks": [
                "Existing invalid input may behave differently"
            ]
        }
        """
    )

    writer = FakeTool(
        name="code_writer",
        result={
            "success": True,
            "files_written": [
                "app/parser.py"
            ],
        },
    )

    registry = FakeRegistry(
        {
            "code_writer": writer,
        }
    )

    context = {
        "task": "Implement parser validation",
        "strategy": {
            "type": "development",
            "repository_analysis_fallback": False,
        },
    }

    agent = CodeAgent(
        llm,
        registry,
    )

    result = agent.run(
        "Implement parser validation",
        development_context=context,
    )

    assert result["success"] is True

    assert result["write_result"] == {
        "success": True,
        "files_written": [
            "app/parser.py"
        ],
    }

    assert len(writer.calls) == 1

    writer_input = writer.calls[0]["args"][0]

    assert writer_input["summary"] == (
        "Implement parser validation"
    )

    assert writer_input["files"] == [
        {
            "path": "app/parser.py",
            "purpose": "Add validation",
            "changes": [
                "Validate parser input"
            ],
        }
    ]

    assert writer_input["development_context"] == context


@pytest.mark.unit
def test_code_agent_uses_development_context_builder():
    llm = FakeLLM(
        response="""
        {
            "summary": "Fix parser",
            "files": [],
            "implementation": [],
            "risks": []
        }
        """
    )

    writer = FakeTool(
        name="code_writer",
        result={
            "success": True,
        },
    )

    registry = FakeRegistry(
        {
            "code_writer": writer,
        }
    )

    context = {
        "task": "Fix parser",
        "strategy": {
            "type": "development",
            "repository_analysis_fallback": False,
        },
    }

    development_context = FakeDevelopmentContext(
        context
    )

    agent = CodeAgent(
        llm,
        registry,
        development_context=development_context,
    )

    result = agent.run(
        "Fix parser"
    )

    assert result["success"] is True

    assert development_context.calls == [
        "Fix parser"
    ]

    writer_input = writer.calls[0]["args"][0]

    assert writer_input["development_context"] == context


@pytest.mark.unit
def test_code_agent_builds_development_context_when_not_provided():
    llm = FakeLLM(
        response="""
        {
            "summary": "Fix parser",
            "files": [],
            "implementation": [],
            "risks": []
        }
        """
    )

    writer = FakeTool(
        name="code_writer",
        result={
            "success": True,
        },
    )

    registry = FakeRegistry(
        {
            "code_writer": writer,
        }
    )

    context = {
        "task": "Fix parser",
        "strategy": {
            "type": "development",
            "repository_analysis_fallback": False,
        },
    }

    development_context = FakeDevelopmentContext(
        context
    )

    agent = CodeAgent(
        llm,
        registry,
        development_context=development_context,
    )

    result = agent.run(
        "Fix parser"
    )

    assert result["success"] is True

    assert development_context.calls == [
        "Fix parser"
    ]


@pytest.mark.unit
def test_code_agent_uses_explicit_development_context():
    llm = FakeLLM(
        response="""
        {
            "summary": "Fix parser",
            "files": [],
            "implementation": [],
            "risks": []
        }
        """
    )

    writer = FakeTool(
        name="code_writer",
        result={
            "success": True,
        },
    )

    registry = FakeRegistry(
        {
            "code_writer": writer,
        }
    )

    builder_context = FakeDevelopmentContext(
        {
            "task": "Builder context",
        }
    )

    agent = CodeAgent(
        llm,
        registry,
        development_context=builder_context,
    )

    explicit_context = {
        "task": "Explicit context",
        "strategy": {
            "type": "development",
            "repository_analysis_fallback": False,
        },
    }

    result = agent.run(
        "Fix parser",
        development_context=explicit_context,
    )

    assert result["success"] is True

    assert builder_context.calls == []


@pytest.mark.unit
def test_code_agent_context_builder_failure_uses_legacy_context():
    llm = FakeLLM(
        response="""
        {
            "summary": "Fix parser",
            "files": [],
            "implementation": [],
            "risks": []
        }
        """
    )

    writer = FakeTool(
        name="code_writer",
        result={
            "success": True,
        },
    )

    registry = FakeRegistry(
        {
            "code_writer": writer,
        }
    )

    class FailingDevelopmentContext:
        def build(self, task):
            raise RuntimeError(
                "context build failed"
            )

    agent = CodeAgent(
        llm,
        registry,
        development_context=FailingDevelopmentContext(),
    )

    result = agent.run(
        "Fix parser"
    )

    assert result["success"] is True

    writer_input = writer.calls[0]["args"][0]

    assert writer_input["development_context"] == {
        "task": "Fix parser",
        "strategy": {
            "type": "legacy_development",
            "repository_analysis_fallback": True,
        },
    }


@pytest.mark.unit
def test_code_agent_repository_analyzer_runs_when_fallback_enabled():
    llm = FakeLLM(
        response="""
        {
            "summary": "Fix parser",
            "files": [],
            "implementation": [],
            "risks": []
        }
        """
    )

    writer = FakeTool(
        name="code_writer",
        result={
            "success": True,
        },
    )

    analyzer = FakeTool(
        name="repository_analyzer",
        result={
            "files": [
                "app/parser.py",
            ],
            "architecture": "layered",
        },
    )

    registry = FakeRegistry(
        {
            "code_writer": writer,
            "repository_analyzer": analyzer,
        }
    )

    context = {
        "task": "Fix parser",
        "strategy": {
            "type": "development",
            "repository_analysis_fallback": True,
        },
        "architecture": {},
    }

    agent = CodeAgent(
        llm,
        registry,
    )

    result = agent.run(
        "Fix parser",
        development_context=context,
    )

    assert result["success"] is True

    assert analyzer.call_count == 1

    assert analyzer.calls[0]["args"] == (
        {
            "action": "analyze",
        },
    )

    writer_input = writer.calls[0]["args"][0]

    assert writer_input["development_context"] == context


@pytest.mark.unit
def test_code_agent_skips_repository_analyzer_when_analysis_exists():
    llm = FakeLLM(
        response="""
        {
            "summary": "Fix parser",
            "files": [],
            "implementation": [],
            "risks": []
        }
        """
    )

    writer = FakeTool(
        name="code_writer",
        result={
            "success": True,
        },
    )

    analyzer = FakeTool(
        name="repository_analyzer",
        result={
            "files": [
                "should_not_be_used.py",
            ],
        },
    )

    registry = FakeRegistry(
        {
            "code_writer": writer,
            "repository_analyzer": analyzer,
        }
    )

    context = {
        "task": "Fix parser",
        "strategy": {
            "type": "development",
            "repository_analysis_fallback": True,
        },
        "architecture": {
            "repository_analysis": {
                "files": [
                    "existing.py",
                ],
            }
        },
    }

    agent = CodeAgent(
        llm,
        registry,
    )

    result = agent.run(
        "Fix parser",
        development_context=context,
    )

    assert result["success"] is True

    assert analyzer.call_count == 0

    writer_input = writer.calls[0]["args"][0]

    assert writer_input["development_context"] == context


@pytest.mark.unit
def test_code_agent_handles_missing_repository_analyzer():
    llm = FakeLLM(
        response="""
        {
            "summary": "Fix parser",
            "files": [],
            "implementation": [],
            "risks": []
        }
        """
    )

    writer = FakeTool(
        name="code_writer",
        result={
            "success": True,
        },
    )

    registry = FakeRegistry(
        {
            "code_writer": writer,
        }
    )

    context = {
        "task": "Fix parser",
        "strategy": {
            "type": "development",
            "repository_analysis_fallback": True,
        },
        "architecture": {},
    }

    agent = CodeAgent(
        llm,
        registry,
    )

    result = agent.run(
        "Fix parser",
        development_context=context,
    )

    assert result["success"] is True

    assert writer.call_count == 1

    writer_input = writer.calls[0]["args"][0]

    assert writer_input["development_context"]["architecture"] == {}

@pytest.mark.unit
def test_code_agent_returns_failure_when_llm_raises():
    class FailingLLM:
        def generate(
            self,
            prompt,
            max_tokens=None,
            temperature=None,
            timeout=None,
        ):
            raise RuntimeError("LLM unavailable")

    agent = CodeAgent(
        FailingLLM(),
        FakeRegistry(),
    )

    result = agent.run(
        "Fix parser"
    )

    assert result == {
        "success": False,
        "error": "LLM unavailable",
    }


@pytest.mark.unit
def test_code_agent_returns_failure_when_llm_returns_dict():
    llm = FakeLLM(
        response={
            "error": "model unavailable",
        }
    )

    agent = CodeAgent(
        llm,
        FakeRegistry(),
    )

    result = agent.run(
        "Fix parser"
    )

    assert result == {
        "success": False,
        "error": "Code Agent LLM request failed.",
        "details": {
            "error": "model unavailable",
        },
    }


@pytest.mark.unit
def test_code_agent_returns_failure_when_llm_returns_invalid_type():
    llm = FakeLLM(
        response=12345
    )

    agent = CodeAgent(
        llm,
        FakeRegistry(),
    )

    result = agent.run(
        "Fix parser"
    )

    assert result == {
        "success": False,
        "error": "Unexpected LLM response type.",
    }


@pytest.mark.unit
def test_code_agent_returns_failure_when_json_repair_fails():
    class RepairFailingLLM:
        def __init__(self):
            self.calls = []

        def generate(
            self,
            prompt,
            max_tokens=None,
            temperature=None,
            timeout=None,
        ):
            self.calls.append(prompt)

            if len(self.calls) == 1:
                return "This is not valid JSON"

            raise RuntimeError(
                "repair unavailable"
            )

    llm = RepairFailingLLM()

    agent = CodeAgent(
        llm,
        FakeRegistry(),
    )

    result = agent.run(
        "Fix parser"
    )

    assert result["success"] is False
    assert result["error"] == (
        "LLM returned invalid JSON."
    )
    assert result["raw"] == (
        "This is not valid JSON"
    )

    assert len(llm.calls) == 2


@pytest.mark.unit
def test_code_agent_uses_repaired_json_plan():
    class RepairingLLM:
        def __init__(self):
            self.calls = []

        def generate(
            self,
            prompt,
            max_tokens=None,
            temperature=None,
            timeout=None,
        ):
            self.calls.append(prompt)

            if len(self.calls) == 1:
                return """
                {
                    "summary": "broken plan",
                    "files": [
                """

            return """
            {
                "summary": "Repaired plan",
                "files": [
                    {
                        "path": "app/parser.py",
                        "purpose": "Fix parser",
                        "changes": [
                            "Add validation"
                        ]
                    }
                ],
                "implementation": [
                    "Validate parser input"
                ],
                "risks": []
            }
            """

    writer = FakeTool(
        name="code_writer",
        result={
            "success": True,
        },
    )

    registry = FakeRegistry(
        {
            "code_writer": writer,
        }
    )

    llm = RepairingLLM()

    agent = CodeAgent(
        llm,
        registry,
    )

    result = agent.run(
        "Fix parser"
    )

    assert result["success"] is True

    assert len(llm.calls) == 2

    assert result["plan"]["summary"] == (
        "Repaired plan"
    )

    assert result["plan"]["files"] == [
        {
            "path": "app/parser.py",
            "purpose": "Fix parser",
            "changes": [
                "Add validation"
            ],
        }
    ]

    assert result["plan"]["implementation"] == [
        "Validate parser input"
    ]

    assert writer.call_count == 1


@pytest.mark.unit
def test_code_agent_returns_failure_when_code_writer_is_missing():
    llm = FakeLLM(
        response="""
        {
            "summary": "Fix parser",
            "files": [],
            "implementation": [],
            "risks": []
        }
        """
    )

    registry = FakeRegistry()

    agent = CodeAgent(
        llm,
        registry,
    )

    result = agent.run(
        "Fix parser"
    )

    assert result["success"] is False

    assert result["error"] == (
        "Code writer unavailable."
    )

    assert result["plan"] == {
        "summary": "Fix parser",
        "files": [],
        "implementation": [],
        "risks": [],
    }


@pytest.mark.unit
def test_code_agent_returns_failure_when_code_writer_raises():
    llm = FakeLLM(
        response="""
        {
            "summary": "Fix parser",
            "files": [],
            "implementation": [],
            "risks": []
        }
        """
    )

    class FailingWriter:
        def execute(self, plan):
            raise RuntimeError(
                "writer failed"
            )

    registry = FakeRegistry(
        {
            "code_writer": FailingWriter(),
        }
    )

    agent = CodeAgent(
        llm,
        registry,
    )

    result = agent.run(
        "Fix parser"
    )

    assert result["success"] is False

    assert result["error"] == (
        "writer failed"
    )

    assert result["plan"]["summary"] == (
        "Fix parser"
    )

    assert (
        result["plan"]["development_context"][
            "task"
        ]
        == "Fix parser"
    )


@pytest.mark.unit
def test_code_agent_returns_writer_failure_result():
    llm = FakeLLM(
        response="""
        {
            "summary": "Fix parser",
            "files": [],
            "implementation": [],
            "risks": []
        }
        """
    )

    writer = FakeTool(
        name="code_writer",
        result={
            "success": False,
            "error": "Unable to write file",
        },
    )

    registry = FakeRegistry(
        {
            "code_writer": writer,
        }
    )

    agent = CodeAgent(
        llm,
        registry,
    )

    result = agent.run(
        "Fix parser"
    )

    assert result["success"] is False

    assert result["write_result"] == {
        "success": False,
        "error": "Unable to write file",
    }

    assert result["plan"]["summary"] == (
        "Fix parser"
    )

@pytest.mark.unit
def test_code_agent_returns_files_written_from_code_writer():
    llm = FakeLLM(
        response="""
        {
            "summary": "Fix parser",
            "files": [
                {
                    "path": "app/parser.py",
                    "purpose": "Fix parser",
                    "changes": [
                        "Add validation"
                    ]
                },
                {
                    "path": "app/tokenizer.py",
                    "purpose": "Fix tokenizer",
                    "changes": [
                        "Handle empty input"
                    ]
                }
            ],
            "implementation": [
                "Update parser",
                "Update tokenizer"
            ],
            "risks": []
        }
        """
    )

    writer = FakeTool(
        name="code_writer",
        result={
            "success": True,
            "results": [
                {
                    "file": "app/parser.py",
                    "status": "updated",
                },
                {
                    "file": "app/tokenizer.py",
                    "status": "updated",
                },
            ],
            "files_written": [
                "app/parser.py",
                "app/tokenizer.py",
            ],
        },
    )

    registry = FakeRegistry(
        {
            "code_writer": writer,
        }
    )

    agent = CodeAgent(
        llm,
        registry,
    )

    result = agent.run(
        "Fix parser"
    )

    assert result["success"] is True

    assert result["write_result"]["files_written"] == [
        "app/parser.py",
        "app/tokenizer.py",
    ]

@pytest.mark.unit
def test_code_agent_stores_repository_analysis_in_development_context():
    llm = FakeLLM(
        response="""
        {
            "summary": "Fix parser",
            "files": [],
            "implementation": [],
            "risks": []
        }
        """
    )

    writer = FakeTool(
        name="code_writer",
        result={
            "success": True,
        },
    )

    analyzer = FakeTool(
        name="repository_analyzer",
        result={
            "files": [
                "app/parser.py",
                "app/tokenizer.py",
            ],
            "architecture": "layered",
        },
    )

    registry = FakeRegistry(
        {
            "code_writer": writer,
            "repository_analyzer": analyzer,
        }
    )

    context = {
        "task": "Fix parser",
        "strategy": {
            "type": "development",
            "repository_analysis_fallback": True,
        },
        "architecture": {},
    }

    agent = CodeAgent(
        llm,
        registry,
    )

    result = agent.run(
        "Fix parser",
        development_context=context,
    )

    assert result["success"] is True

    writer_input = writer.calls[0]["args"][0]

    development_context = (
        writer_input["development_context"]
    )

    assert development_context["architecture"][
        "repository_analysis"
    ] == {
        "files": [
            "app/parser.py",
            "app/tokenizer.py",
        ],
        "architecture": "layered",
    }

@pytest.mark.unit
def test_code_agent_repository_context_handles_missing_architecture():

    agent = CodeAgent(
        llm=FakeLLM(),
        registry=FakeRegistry(),
    )

    agent._analyze_repository = lambda: {
        "files": ["app/main.py"],
    }

    context = {
        "strategy": {
            "repository_analysis_fallback": True,
        },
        "architecture": None,
    }

    result = agent._get_repository_context(context)

    assert result == str(
        {
            "files": ["app/main.py"],
        }
    )

    assert context["architecture"] == {
        "repository_analysis": {
            "files": ["app/main.py"],
        }
    }