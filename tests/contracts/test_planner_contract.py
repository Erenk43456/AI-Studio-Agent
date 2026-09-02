import pytest

from contracts.planner_contract import PlannerContract
from agents.planner_agent import PlannerAgent
from tests.fakes.fake_model_provider import FakeModelProvider


class DummyPlanner(PlannerContract):
    def create_plan(self, task: str) -> dict:
        return {"steps": [{"tool": "code", "action": "implement", "input": task}]}


@pytest.mark.contract
def test_dummy_planner_satisfies_planner_contract():
    planner = DummyPlanner()
    assert isinstance(planner, PlannerContract)
    assert callable(planner.create_plan)
    plan = planner.create_plan("test task")
    assert isinstance(plan, dict)
    assert "steps" in plan


@pytest.mark.contract
def test_planner_agent_satisfies_planner_contract():
    llm = FakeModelProvider()
    agent = PlannerAgent(llm=llm)
    assert isinstance(agent, PlannerContract)
    assert callable(agent.create_plan)
