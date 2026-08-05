from app.core.logger import AppLogger


class DevelopmentOrchestrator:


    def __init__(
        self,
        container
    ):


        self.container = container

        self.planner = container.planner

        self.code_agent = container.code_agent

        self.repository_analyzer = (
            container.repository_analyzer
        )

        self.improvement_agent = (
            container.improvement_agent
        )

        self.logger = AppLogger()



    def run(
        self,
        message,
        decision=None,
        conversation=None
    ):


        self.logger.info(
            f"Development request: {message}"
        )


        if decision is None:

            decision = {
                "action": "code"
            }



        action = decision.get(
            "action",
            "code"
        )



        if action == "analyze":


            return self.repository_analyzer.execute(
                {
                    "action": "analyze"
                }
            )



        if action == "improve":


            return self.improvement_agent.execute(
                message
            )



        return self.execute_code_task(
            message
        )




    def execute_code_task(
        self,
        message
    ):


        plan = self.planner.create_plan(
            message
        )


        if not plan:

            return {
                "success": False,
                "message": "Planner failed."
            }



        steps = plan.get(
            "steps",
            []
        )



        if (

            len(steps) == 1

            and

            steps[0].get("tool") == "code"

        ):


            return self.code_agent.run(

                steps[0].get(
                    "input",
                    message
                )

            )



        return {

            "success": True,

            "plan": plan

        }