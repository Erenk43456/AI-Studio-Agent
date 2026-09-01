import pytest

from agents.planner_agent import PlannerAgent
from agents.tool_agent import ToolAgent
from app.core.orchestrators.development_orchestrator import (
    DevelopmentOrchestrator,
)
from app.core.development_context import DevelopmentContext
from tests.fakes.fake_code_agent import FakeCodeAgent
from tests.fakes.fake_development_context import FakeDevelopmentContext
from tests.fakes.fake_llm import FakeLLM
from tests.fakes.fake_project_memory import FakeProjectMemory
from tests.fakes.fake_registry import FakeRegistry
from tests.fakes.fake_repository_analyzer import FakeRepositoryAnalyzer


class FakeProjectMemorySync:
    def __init__(self):
        self.calls = []

    def sync(self, changed_files=None):
        self.calls.append(changed_files)

        return {
            "success": True,
        }


class FakeContainer:
    def __init__(
        self,
        planner,
        code_agent,
        development_context,
        registry,
        project_memory_sync=None,
    ):
        self.planner = planner
        self.code_agent = code_agent

        self.code_llm = FakeLLM(response="")

        self.development_context = development_context
        self.registry = registry

        self.repository_analyzer = registry.get("repository_analyzer")

        self.tool_agent = ToolAgent(
            registry=registry,
            code_agent=code_agent,
        )

        self.project_memory_sync = project_memory_sync or FakeProjectMemorySync()

        self.improvement_agent = None


@pytest.mark.integration
def test_development_pipeline_executes_code_task():
    llm = FakeLLM(response="""
        {
            "steps": [
                {
                    "tool": "code",
                    "action": "implement",
                    "input": "Fix parser"
                }
            ]
        }
        """)

    registry = FakeRegistry(
        tools={
            "code": object(),
            "repository_analyzer": FakeRepositoryAnalyzer(
                analysis={"success": True, "action": "analyze"}
            ),
        }
    )

    planner = PlannerAgent(
        llm,
        registry=registry,
    )

    code_agent = FakeCodeAgent()

    development_context = FakeDevelopmentContext()

    container = FakeContainer(
        planner=planner,
        code_agent=code_agent,
        development_context=(development_context),
        registry=registry,
    )

    orchestrator = DevelopmentOrchestrator(container)

    result = orchestrator.run("Fix parser")

    assert result == ("✅ Kod başarıyla güncellendi.")

    assert development_context.calls == [
        "Fix parser",
    ]

    assert len(llm.calls) == 1

    assert code_agent.calls == [
        (
            "Fix parser",
            {
                "task": "Fix parser",
                "strategy": {
                    "type": "development",
                    "repository_analysis_fallback": False,
                },
            },
        )
    ]


@pytest.mark.integration
def test_development_pipeline_executes_repository_analysis():
    llm = FakeLLM(response="""
        {
            "steps": [
                {
                    "tool": "repository_analyzer",
                    "action": "analyze",
                    "input": "Analyze repository"
                }
            ]
        }
        """)

    registry = FakeRegistry(
        tools={
            "code": object(),
            "repository_analyzer": FakeRepositoryAnalyzer(
                analysis={"success": True, "action": "analyze"}
            ),
        }
    )

    planner = PlannerAgent(
        llm,
        registry=registry,
    )

    code_agent = FakeCodeAgent()

    development_context = FakeDevelopmentContext()

    container = FakeContainer(
        planner=planner,
        code_agent=code_agent,
        development_context=(development_context),
        registry=registry,
    )

    orchestrator = DevelopmentOrchestrator(container)

    result = orchestrator.run("Analyze repository")

    assert result == ("✅ İşlem başarıyla tamamlandı.")

    assert registry.calls == [
        "repository_analyzer",
        "repository_analyzer",
        "repository_analyzer",
    ]

    assert development_context.calls == [
        "Analyze repository",
    ]

    assert code_agent.calls == []


@pytest.mark.integration
def test_development_pipeline_executes_multiple_steps_in_order():
    llm = FakeLLM(response="""
        {
            "steps": [
                {
                    "tool": "repository_analyzer",
                    "action": "analyze",
                    "input": "Analyze repository"
                },
                {
                    "tool": "code",
                    "action": "implement",
                    "input": "Fix parser"
                }
            ]
        }
        """)

    registry = FakeRegistry(
        tools={
            "code": object(),
            "repository_analyzer": FakeRepositoryAnalyzer(
                analysis={"success": True, "action": "analyze"}
            ),
        }
    )

    planner = PlannerAgent(
        llm,
        registry=registry,
    )

    code_agent = FakeCodeAgent()

    development_context = FakeDevelopmentContext()

    container = FakeContainer(
        planner=planner,
        code_agent=code_agent,
        development_context=(development_context),
        registry=registry,
    )

    orchestrator = DevelopmentOrchestrator(container)

    result = orchestrator.run("Analyze repository and fix parser")

    assert result == (
        "✅ İşlem başarıyla tamamlandı.\n\n" "✅ Kod başarıyla güncellendi."
    )

    assert development_context.calls == [
        "Analyze repository and fix parser",
    ]

    assert code_agent.calls == [
        (
            "Fix parser",
            {
                "task": "Analyze repository and fix parser",
                "strategy": {
                    "type": "development",
                    "repository_analysis_fallback": False,
                },
            },
        )
    ]

    assert registry.calls == [
        "repository_analyzer",
        "repository_analyzer",
        "code",
        "repository_analyzer",
    ]

    assert len(llm.calls) == 1


@pytest.mark.integration
def test_development_pipeline_passes_architecture_aware_context_to_code_agent():
    llm = FakeLLM(response="""
        {
            "steps": [
                {
                    "tool": "code",
                    "action": "implement",
                    "input": "Fix app/core/parser.py"
                }
            ]
        }
        """)

    files = {
        "app/core/parser.py": {
            "imports": ["app/core/tokenizer.py"],
            "summary": "Parser implementation",
        },
        "app/core/tokenizer.py": {
            "summary": "Tokenizer used by parser",
        },
        "tools/unrelated.py": {
            "summary": "Unrelated utility",
        },
    }

    architecture = {
        "components": [
            "app/core/parser.py",
            "app/core/tokenizer.py",
        ],
    }

    class FakeProjectMemory:
        def get_all_files(self):
            return files

        def get_file(self, path):
            return files.get(path)

        def get_architecture(self):
            return architecture

    planner = PlannerAgent(
        llm,
        registry=FakeRegistry(
            tools={
                "code": object(),
                "repository_analyzer": FakeRepositoryAnalyzer(
                analysis={"success": True, "action": "analyze"}
            ),
            }
        ),
    )

    code_agent = FakeCodeAgent()

    development_context = DevelopmentContext(
        FakeProjectMemory(),
        "C:/AI-Studio",
    )

    container = FakeContainer(
        planner=planner,
        code_agent=code_agent,
        development_context=development_context,
        registry=FakeRegistry(
            tools={
                "code": object(),
                "repository_analyzer": FakeRepositoryAnalyzer(
                analysis={"success": True, "action": "analyze"}
            ),
            }
        ),
    )

    orchestrator = DevelopmentOrchestrator(container)

    result = orchestrator.run("Fix app/core/parser.py")

    assert result == ("✅ Kod başarıyla güncellendi.")

    assert len(code_agent.calls) == 1

    passed_context = code_agent.calls[0][1]

    assert passed_context["task"] == ("Fix app/core/parser.py")

    assert passed_context["targets"] == ["app/core/parser.py"]

    assert passed_context["target_files"] == {
        "app/core/parser.py": files["app/core/parser.py"]
    }

    assert "app/core/tokenizer.py" in (passed_context["related_files"])

    assert "app/core/parser.py" not in (passed_context["related_files"])

    assert passed_context["strategy"]["type"] == ("architecture_aware_targeted_fix")

    assert passed_context["strategy"]["architecture_aware"] is True

    assert passed_context["strategy"]["minimal_change"] is True


@pytest.mark.integration
def test_development_pipeline_runs_repository_analysis_fallback_when_memory_is_unavailable():

    llm = FakeLLM(response="""
        {
            "steps": [
                {
                    "tool": "code",
                    "action": "implement",
                    "input": "Fix parser"
                }
            ]
        }
        """)

    registry = FakeRegistry(
        tools={
            "code": object(),
            "repository_analyzer": FakeRepositoryAnalyzer(
                analysis={"success": True, "action": "analyze"}
            ),
        }
    )

    planner = PlannerAgent(
        llm,
        registry=registry,
    )

    code_agent = FakeCodeAgent()

    development_context = FakeDevelopmentContext(fallback=True)

    project_memory_sync = FakeProjectMemorySync()

    container = FakeContainer(
        planner=planner,
        code_agent=code_agent,
        development_context=(development_context),
        registry=registry,
        project_memory_sync=(project_memory_sync),
    )

    orchestrator = DevelopmentOrchestrator(container)

    result = orchestrator.run("Fix parser")

    assert result == ("✅ Kod başarıyla güncellendi.")

    assert development_context.calls == [
        "Fix parser",
        "Fix parser",
    ]

    assert project_memory_sync.calls == [["app/core/parser.py"]]

    assert len(code_agent.calls) == 1
