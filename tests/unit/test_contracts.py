import pytest
from agents.contracts import (
    DecisionContract,
    PlannerStep,
    PlannerContract,
    ToolStepContract,
    ToolResultContract,
    MemoryContract,
)
from agents.contract_agent import ContractAgent


@pytest.fixture
def contract_agent():
    return ContractAgent()


# =============================================================
# DecisionContract Tests
# =============================================================

@pytest.mark.unit
def test_decision_contract_defaults():
    decision = DecisionContract(system="development")
    assert decision.system == "development"
    assert decision.action == ""
    assert decision.reason == ""
    assert decision.metadata == {}


@pytest.mark.unit
def test_contract_agent_to_decision_contract_from_dict(contract_agent):
    data = {
        "system": "memory",
        "action": "save",
        "reason": "user requested name save",
        "key": "user_name",
        "value": "Eren",
    }
    decision = contract_agent.to_decision_contract(data)
    assert isinstance(decision, DecisionContract)
    assert decision.system == "memory"
    assert decision.action == "save"
    assert decision.reason == "user requested name save"
    assert decision.metadata.get("key") == "user_name"
    assert decision.metadata.get("value") == "Eren"


@pytest.mark.unit
def test_contract_agent_to_decision_contract_invalid_system_fallback(contract_agent):
    data = {"system": "invalid_sys", "reason": "unknown"}
    decision = contract_agent.to_decision_contract(data, default_system="chat")
    assert decision.system == "chat"


# =============================================================
# PlannerContract & PlannerStep Tests
# =============================================================

@pytest.mark.unit
def test_planner_step_defaults():
    step = PlannerStep(tool="code", action="implement")
    assert step.tool == "code"
    assert step.action == "implement"
    assert step.input == ""
    assert step.parameters == {}
    assert step.context == {}


@pytest.mark.unit
def test_contract_agent_to_planner_contract_from_dict(contract_agent):
    raw = {
        "steps": [
            {
                "tool": "repository_analyzer",
                "action": "analyze",
                "input": "Analyze repo",
            },
            {
                "tool": "code",
                "action": "implement",
                "input": "Fix bug",
                "filename": "app/main.py",
            },
        ],
        "user_message": "Fix the bug in main.py",
    }
    plan = contract_agent.to_planner_contract(raw)
    assert isinstance(plan, PlannerContract)
    assert len(plan.steps) == 2
    assert plan.user_message == "Fix the bug in main.py"

    step0 = plan.steps[0]
    assert isinstance(step0, PlannerStep)
    assert step0.tool == "repository_analyzer"
    assert step0.action == "analyze"
    assert step0.input == "Analyze repo"

    step1 = plan.steps[1]
    assert step1.tool == "code"
    assert step1.action == "implement"
    assert step1.parameters.get("filename") == "app/main.py"


@pytest.mark.unit
def test_contract_agent_to_planner_contract_single_step(contract_agent):
    raw = {
        "tool": "calculator",
        "action": "execute",
        "input": "2 + 2",
    }
    plan = contract_agent.to_planner_contract(raw, user_message="calc 2+2")
    assert len(plan.steps) == 1
    assert plan.steps[0].tool == "calculator"
    assert plan.steps[0].action == "execute"
    assert plan.steps[0].input == "2 + 2"


# =============================================================
# ToolStepContract Tests
# =============================================================

@pytest.mark.unit
def test_contract_agent_to_tool_step_contract(contract_agent):
    step = PlannerStep(
        tool="file",
        action="read",
        input="test.py",
        parameters={"path": "test.py"},
    )
    tool_step = contract_agent.to_tool_step_contract(step)
    assert isinstance(tool_step, ToolStepContract)
    assert tool_step.tool == "file"
    assert tool_step.action == "read"
    assert tool_step.input == "test.py"
    assert tool_step.parameters == {"path": "test.py"}


# =============================================================
# ToolResultContract Tests
# =============================================================

@pytest.mark.unit
def test_contract_agent_to_tool_result_from_str(contract_agent):
    result = contract_agent.to_tool_result_contract("success output")
    assert isinstance(result, ToolResultContract)
    assert result.success is True
    assert result.data == "success output"
    assert result.message == "success output"


@pytest.mark.unit
def test_contract_agent_to_tool_result_from_dict(contract_agent):
    data = {
        "success": False,
        "error": "File not found",
        "code": 404,
    }
    result = contract_agent.to_tool_result_contract(data)
    assert isinstance(result, ToolResultContract)
    assert result.success is False
    assert result.error == "File not found"
    assert result.metadata.get("code") == 404


@pytest.mark.unit
def test_contract_agent_to_tool_result_from_exception(contract_agent):
    err = ValueError("Invalid operation")
    result = contract_agent.to_tool_result_contract(err)
    assert isinstance(result, ToolResultContract)
    assert result.success is False
    assert "Invalid operation" in result.error


# =============================================================
# MemoryContract Tests
# =============================================================

@pytest.mark.unit
def test_contract_agent_to_memory_contract(contract_agent):
    data = {
        "action": "save",
        "key": "user_name",
        "value": "Eren",
        "category": "personal",
    }
    memory = contract_agent.to_memory_contract(data)
    assert isinstance(memory, MemoryContract)
    assert memory.action == "save"
    assert memory.key == "user_name"
    assert memory.value == "Eren"
    assert memory.category == "personal"
