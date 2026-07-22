from agents.base_agent import BaseAgent
from models.llm import LLM


from agents.planner.calculator_parser import parse_calculator
from agents.planner.memory_parser import parse_memory
from agents.planner.greeting_parser import parse_greeting
from agents.planner.llm_planner import create_llm_plan




class PlannerAgent(BaseAgent):


    def __init__(
        self,
        memory=None
    ):

        super().__init__(
            "Planner Agent",
            memory
        )


        self.llm = LLM()





    def create_plan(
        self,
        task
    ):


        task = task.lower().strip()





        greeting_plan = parse_greeting(
            task
        )


        if greeting_plan:

            return greeting_plan





        calculator_plan = parse_calculator(
            task
        )


        if calculator_plan:

            return calculator_plan





        memory_plan = parse_memory(
            task
        )


        if memory_plan:

            return memory_plan






        if self.memory:


            self.memory.save(

                "last_task",

                task,

                "system"

            )





        return create_llm_plan(

            self.llm,

            task

        )