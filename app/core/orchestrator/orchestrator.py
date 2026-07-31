from app.core.logger import AppLogger



class Orchestrator:


    def __init__(
        self,
        planner,
        agents
    ):

        self.planner = planner

        self.agents = agents

        self.logger = AppLogger()





    def run(
        self,
        message,
        conversation=None
    ):


        self.logger.info(
            f"Processing request: {message}"
        )



        plan = self.planner.create_plan(
            message
        )



        print("\n===== GENERATED PLAN =====")
        print(plan)
        print("==========================\n")



        if not plan:

            return "Planner failed to create a plan."





        steps = plan.get(
            "steps",
            []
        )



        tool_name = plan.get(
            "tool"
        )





        # -------------------------
        # Direct single action
        # -------------------------

        if not steps:


            if tool_name == "chat":


                agent = self.agents.get(
                    "chat"
                )


                if not agent:

                    return "Chat agent not available."



                return agent.chat(
                    message
                )




            agent = self.agents.get(
                "tool"
            )


            if not agent:

                return "Tool agent not available."



            return agent.execute(
                plan
            )







        # -------------------------
        # Multi step workflow
        # -------------------------

        if (

            len(steps) == 1

            and steps[0].get("tool") == "chat"

        ):


            agent = self.agents.get(
                "chat"
            )


            if not agent:

                return "Chat agent not available."



            return agent.chat(
                message
            )







        agent = self.agents.get(
            "tool"
        )


        if not agent:

            return "Tool agent not available."



        return agent.execute_steps(
            plan
        )