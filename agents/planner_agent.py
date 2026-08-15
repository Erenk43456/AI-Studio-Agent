from agents.base_agent import BaseAgent

from app.core.logger import AppLogger


from agents.planner.llm_planner import create_llm_plan



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

        if not original_task:

            return {
                "steps": [
                    {
                        "tool": "chat",
                        "action": "chat",
                        "input": ""
                    }
                ]
            }

        # 
        # Save last task
        #

        if self.memory:

            self.memory.save(
                "last_task",
                original_task,
                "system"
            )

        #
        # Tool descriptions
        #

        tool_descriptions = None 

        if self.registry:

            tool_descriptions = (
                self.registry.get_tool_descriptions()
            )

        #
        # LLM Planner
        #

        try:

            plan = create_llm_plan(
                self.llm,
                original_task,
                tool_descriptions
            )

            if isinstance(
                plan,
                dict
            ):

                plan["user_message"] = (
                    original_task
                )

                return plan

            #
            # Invalid planner result
            #

            return {
                "steps": [
                    {
                        "tool": "chat",
                        "action": "chat",
                        "input": original_task
                    }
                ],
                "user_message": original_task
            }

        except Exception as error:

            self.logger.error(
                f"Planner error: {error}"
            )

            return {
                "steps": [
                    {
                        "tool": "chat",
                        "action": "chat",
                        "input": original_task
                    }
                ],
                "user_message": original_task
            }