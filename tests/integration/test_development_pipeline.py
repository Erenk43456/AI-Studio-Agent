import pytest

from agents.planner_agent import PlannerAgent
from app.core.orchestrators.development_orchestrator import (
    DevelopmentOrchestrator,
)


class FakeLLM:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def generate(self, prompt, **kwargs):
        self.calls.append(
            {
                "prompt": prompt,
                "kwargs": kwargs,
            }
        )

        return self.response


class FakeDevelopmentContext:
    def __init__(self):
        self.calls = []

    def build(self, task):
        self.calls.append(task)

        return {
            "task": task,
            "strategy": {
                "type": "development",
                "repository_analysis_fallback": False,
            },
        }


class FakeCodeAgent:
    def __init__(self):
        self.calls = []

    def run(
        self,
        task,
        development_context=None,
    ):
        self.calls.append(
            {
                "task": task,
                "development_context": development_context,
            }
        )

        return {
            "success": True,
            "write_result": {
                "success": True,
                "files_written": [
                    "app/parser.py",
                ],
            },
        }


class FakeRepositoryAnalyzer:
    def execute(self, step):
        return {
            "success": True,
            "action": "analyze",
        }


class FakeRegistry:
    def __init__(self):
        self.tools = {
            "code": object(),
            "repository_analyzer": (
                FakeRepositoryAnalyzer()
            ),
        }

        self.calls = []

    def get(self, name):
        self.calls.append(name)
        return self.tools.get(name)

    def get_tool_descriptions(self):
        return [
            {
                "name": "code",
                "description": "Implement code changes.",
                "purpose": "Modify software.",
            },
            {
                "name": "repository_analyzer",
                "description": "Analyze repository.",
                "purpose": "Analyze the repository.",
            },
        ]


class FakeContainer:
    def __init__(
        self,
        planner,
        code_agent,
        development_context,
        registry,
    ):
        self.planner = planner
        self.code_agent = code_agent
        self.development_context = (
            development_context
        )
        self.registry = registry
        self.repository_analyzer = (
            registry.get(
                "repository_analyzer"
            )
        )
        self.improvement_agent = None


@pytest.mark.integration
def test_development_pipeline_executes_code_task():
    llm = FakeLLM(
        response="""
        {
            "steps": [
                {
                    "tool": "code",
                    "action": "implement",
                    "input": "Fix parser"
                }
            ]
        }
        """
    )

    registry = FakeRegistry()

    planner = PlannerAgent(
        llm,
        registry=registry,
    )

    code_agent = FakeCodeAgent()

    development_context = (
        FakeDevelopmentContext()
    )

    container = FakeContainer(
        planner=planner,
        code_agent=code_agent,
        development_context=(
            development_context
        ),
        registry=registry,
    )

    orchestrator = DevelopmentOrchestrator(
        container
    )

    result = orchestrator.run(
        "Fix parser"
    )

    assert result == (
        "✅ Kod başarıyla güncellendi."
    )

    assert development_context.calls == [
        "Fix parser",
    ]

    assert len(llm.calls) == 1

    assert code_agent.calls == [
        {
            "task": "Fix parser",
            "development_context": {
                "task": "Fix parser",
                "strategy": {
                    "type": "development",
                    "repository_analysis_fallback": False,
                },
            },
        }
    ]


@pytest.mark.integration
def test_development_pipeline_executes_repository_analysis():
    llm = FakeLLM(
        response="""
        {
            "steps": [
                {
                    "tool": "repository_analyzer",
                    "action": "analyze",
                    "input": "Analyze repository"
                }
            ]
        }
        """
    )

    registry = FakeRegistry()

    planner = PlannerAgent(
        llm,
        registry=registry,
    )

    code_agent = FakeCodeAgent()

    development_context = (
        FakeDevelopmentContext()
    )

    container = FakeContainer(
        planner=planner,
        code_agent=code_agent,
        development_context=(
            development_context
        ),
        registry=registry,
    )

    orchestrator = DevelopmentOrchestrator(
        container
    )

    result = orchestrator.run(
        "Analyze repository"
    )

    assert result == (
        "✅ İşlem başarıyla tamamlandı."
    )

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
    llm = FakeLLM(
        response="""
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
        """
    )

    registry = FakeRegistry()

    planner = PlannerAgent(
        llm,
        registry=registry,
    )

    code_agent = FakeCodeAgent()

    development_context = (
        FakeDevelopmentContext()
    )

    container = FakeContainer(
        planner=planner,
        code_agent=code_agent,
        development_context=(
            development_context
        ),
        registry=registry,
    )

    orchestrator = DevelopmentOrchestrator(
        container
    )

    result = orchestrator.run(
        "Analyze repository and fix parser"
    )

    assert result == (
        "✅ İşlem başarıyla tamamlandı.\n\n"
        "✅ Kod başarıyla güncellendi."
    )

    assert development_context.calls == [
        "Analyze repository and fix parser",
    ]

    assert code_agent.calls == [
        {
            "task": "Fix parser",
            "development_context": {
                "task": "Analyze repository and fix parser",
                "strategy": {
                    "type": "development",
                    "repository_analysis_fallback": False,
                },
            },
        }
    ]

    assert registry.calls == [
        "repository_analyzer",
        "repository_analyzer",
        "code",
        "repository_analyzer",
    ]

    assert len(llm.calls) == 1