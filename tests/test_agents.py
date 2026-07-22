from agents.planner_agent import PlannerAgent
from agents.decision_agent import DecisionAgent




class DummyMemory:


    def __init__(self):

        self.data = {}




    def save(
        self,
        key,
        value,
        category="general"
    ):

        self.data[key] = value







#
# PlannerAgent Tests
#


def test_planner_calculator():


    memory = DummyMemory()


    planner = PlannerAgent(
        memory
    )


    plan = planner.create_plan(

        "15 ile 20 topla"

    )


    assert plan["tool"] == "calculator"


    assert plan["operation"] == "add"


    assert plan["numbers"] == [

        15,
        20

    ]








def test_planner_memory_save():


    memory = DummyMemory()


    planner = PlannerAgent(
        memory
    )


    plan = planner.create_plan(

        "Benim adım Eren"

    )


    assert plan["tool"] == "memory_save"


    assert plan["key"] == "isim"


    assert plan["value"] == "eren"









def test_planner_memory_get():


    memory = DummyMemory()


    planner = PlannerAgent(
        memory
    )


    plan = planner.create_plan(

        "ismim ne"

    )


    assert plan["tool"] == "memory_get"


    assert plan["key"] == "isim"









def test_planner_chat():


    memory = DummyMemory()


    planner = PlannerAgent(
        memory
    )


    plan = planner.create_plan(

        "merhaba"

    )


    assert plan["tool"] == "chat"









#
# DecisionAgent Tests
#


def test_decision_name_save():


    memory = DummyMemory()


    decision = DecisionAgent(
        memory
    )


    result = decision.process(

        "Benim adım Eren"

    )


    assert result == "memory_save"









def test_decision_name_get():


    memory = DummyMemory()


    decision = DecisionAgent(
        memory
    )


    result = decision.process(

        "ismim ne"

    )


    assert result == "memory_get"









def test_decision_calculator():


    memory = DummyMemory()


    decision = DecisionAgent(
        memory
    )


    result = decision.process(

        "15 ile 20 topla"

    )


    assert result == "calculator"