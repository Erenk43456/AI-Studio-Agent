from agents.planner_agent import PlannerAgent


planner = PlannerAgent()


plan = planner.create_plan(
    "kodu düzelt def test( print('hello')"
)


print(plan)