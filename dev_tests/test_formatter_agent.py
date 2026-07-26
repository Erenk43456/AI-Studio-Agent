from agents.planner_agent import PlannerAgent


planner = PlannerAgent()


plan = planner.create_plan(
    "formatla def test(): print('Merhaba')"
)


print(plan)