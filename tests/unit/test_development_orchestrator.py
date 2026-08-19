import pytest

from app.core.orchestrators.development_orchestrator import (
    DevelopmentOrchestrator,
)


class FakePlanner:
    def __init__(self, plan):
        self.plan = plan
        self.calls = []

    def create_plan(self, message):
        self.calls.append(message)
        return self.plan


class FakeCodeAgent:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def run(self, message, context):
        self.calls.append((message, context))
        return self.result


class FakeTool:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def execute(self, step):
        self.calls.append(step)
        return self.result


class FakeRepositoryAnalyzer:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def execute(self, step):
        self.calls.append(step)
        return self.result


class FakeImprovementAgent:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def execute(self, message):
        self.calls.append(message)
        return self.result


class FakeContext:
    def __init__(self):
        self.calls = []

    def build(self, message):
        self.calls.append(message)

        return {
            "task": message,
            "strategy": {
                "type": "development",
                "repository_analysis_fallback": False,
            },
        }


class FakeRegistry:
    def __init__(self, tools=None):
        self.tools = tools or {}

    def get(self, name):
        return self.tools.get(name)


class FakeContainer:
    def __init__(
        self,
        plan=None,
        code_result=None,
        tool=None,
        repository_result=None,
        improvement_result=None,
    ):
        self.planner = FakePlanner(plan)
        self.code_agent = FakeCodeAgent(code_result)
        self.repository_analyzer = FakeRepositoryAnalyzer(
            repository_result
        )
        self.improvement_agent = FakeImprovementAgent(
            improvement_result
        )
        self.development_context = FakeContext()
        self.registry = FakeRegistry(
            {"fake_tool": tool} if tool else {}
        )
        self.project_memory_sync = FakeProjectMemorySync()

class FakeProjectMemorySync:
    def __init__(self):
        self.calls = []

    def sync(self, changed_files=None):
        self.calls.append(changed_files)

        return {
            "success": True,
        }


@pytest.mark.unit
def test_development_analyze():

    container = FakeContainer(
        repository_result={
            "success": True,
            "message": "Repository analyzed",
        }
    )

    orchestrator = DevelopmentOrchestrator(container)

    result = orchestrator.run(
        "analyze project",
        {"action": "analyze"},
    )

    assert result == "✅ Repository analyzed"

    assert container.repository_analyzer.calls == [
        {"action": "analyze"}
    ]


@pytest.mark.unit
def test_development_improve():

    container = FakeContainer(
        improvement_result={
            "success": True,
            "message": "Improved",
        }
    )

    orchestrator = DevelopmentOrchestrator(container)

    result = orchestrator.run(
        "improve project",
        {"action": "improve"},
    )

    assert result == "✅ Improved"

    assert container.improvement_agent.calls == [
        "improve project"
    ]


@pytest.mark.unit
def test_development_executes_code_task():

    container = FakeContainer(
        plan={
            "steps": [
                {
                    "tool": "code",
                    "input": "fix bug",
                }
            ]
        },
        code_result={
            "success": True,
            "write_result": {
                "success": True
            },
        },
    )

    orchestrator = DevelopmentOrchestrator(container)

    result = orchestrator.run(
        "fix bug"
    )

    assert result == "✅ Kod başarıyla güncellendi."

    assert container.planner.calls == [
        "fix bug"
    ]

    assert container.development_context.calls == [
        "fix bug"
    ]


@pytest.mark.unit
def test_development_planner_failure():

    container = FakeContainer(
        plan=None
    )

    orchestrator = DevelopmentOrchestrator(container)

    result = orchestrator.run(
        "fix bug"
    )

    assert result == (
        "❌ İstek için bir plan oluşturulamadı."
    )


@pytest.mark.unit
def test_development_empty_plan():

    container = FakeContainer(
        plan={"steps": []}
    )

    orchestrator = DevelopmentOrchestrator(container)

    result = orchestrator.run(
        "fix bug"
    )

    assert result == (
        "❌ Planner herhangi bir işlem oluşturmadı."
    )


@pytest.mark.unit
def test_development_unknown_tool():

    container = FakeContainer(
        plan={
            "steps": [
                {
                    "tool": "missing_tool",
                }
            ]
        }
    )

    orchestrator = DevelopmentOrchestrator(container)

    result = orchestrator.run(
        "do something"
    )

    assert "Tool not found: missing_tool" in result


@pytest.mark.unit
def test_development_tool_execution():

    tool = FakeTool(
        {
            "success": True,
            "message": "Tool executed",
        }
    )

    container = FakeContainer(
        plan={
            "steps": [
                {
                    "tool": "fake_tool",
                    "action": "execute",
                }
            ]
        },
        tool=tool,
    )

    orchestrator = DevelopmentOrchestrator(container)

    result = orchestrator.run(
        "run tool"
    )

    assert result == "✅ Tool executed"

    assert tool.calls == [
        {
            "tool": "fake_tool",
            "action": "execute",
        }
    ]