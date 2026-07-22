from agents.base_agent import BaseAgent
from models.llm import LLM
from app.core.logger import AppLogger


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

        self.logger = AppLogger()







    def create_plan(
        self,
        task
    ):


        task = task.lower().strip()



        self.logger.info(
            f"Creating plan for: {task}"
        )




        try:



            greeting_plan = parse_greeting(
                task
            )


            if greeting_plan:


                self.logger.info(
                    "Plan selected: greeting"
                )


                return greeting_plan






            calculator_plan = parse_calculator(
                task
            )


            if calculator_plan:


                self.logger.info(
                    "Plan selected: calculator"
                )


                return calculator_plan






            memory_plan = parse_memory(
                task
            )


            if memory_plan:


                self.logger.info(
                    "Plan selected: memory"
                )


                return memory_plan








            if self.memory:


                self.memory.save(

                    "last_task",

                    task,

                    "system"

                )








            self.logger.info(
                "No parser matched. Using LLM planner."
            )



            return create_llm_plan(

                self.llm,

                task

            )






        except Exception as error:


            self.logger.error(

                f"Planner error: {error}"

            )


            return {

                "tool": "chat",

                "message": task

            }