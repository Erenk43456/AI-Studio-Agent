from agents.base_agent import BaseAgent

from app.core.logger import AppLogger


from agents.planner.code_repair_parser import parse_code_repair
from agents.planner.formatter_parser import parse_formatter
from agents.planner.calculator_parser import parse_calculator
from agents.planner.memory_parser import parse_memory
from agents.planner.greeting_parser import parse_greeting
from agents.planner.llm_planner import create_llm_plan
from agents.planner.code_analyzer_parser import parse_code_analyzer
from agents.planner.repository_analyzer_parser import parse_repository_analyzer
from agents.planner.file_parser import parse_file
from agents.planner.code_parser import parse_code
from agents.planner.chat_parser import parse_chat



class PlannerAgent(BaseAgent):


    def __init__(
        self,
        llm,
        memory=None,
        registry=None
    ):


        super().__init__(
            "Planner Agent",
            memory
        )


        self.llm = llm

        self.registry = registry


        self.logger = AppLogger()






    def create_plan(
        self,
        task
    ):


        original_task = task.strip()



        self.logger.info(

            f"Creating plan for: {original_task}"

        )





        try:



            parsers = [

                (
                    "code_repair",
                    parse_code_repair
                ),

                (
                    "repository_analyzer",
                    parse_repository_analyzer
                ),

                (
                    "code_analyzer",
                    parse_code_analyzer
                ),

                (
                    "file",
                    parse_file
                ),

                (
                    "code",
                    parse_code
                ),

            ]   






            for name, parser in parsers:


                plan = parser(

                    original_task

                )



                if plan:


                    self.logger.info(

                        f"Plan selected: {name}"

                    )


                    plan["user_message"] = original_task


                    return plan








            if self.memory:


                self.memory.save(

                    "last_task",

                    original_task,

                    "system"

                )







            self.logger.info(

                "No parser matched. Using LLM planner."

            )



            tool_descriptions = None


            if self.registry:


                tool_descriptions = self.registry.get_tool_descriptions()





            plan = create_llm_plan(

                self.llm,

                original_task,

                tool_descriptions

            )







            if isinstance(plan, dict):

                plan["user_message"] = original_task





            return plan







        except Exception as error:


            self.logger.error(

                f"Planner error: {error}"

            )



            return {


                "tool": "chat",


                "message": original_task,


                "user_message": original_task

            }