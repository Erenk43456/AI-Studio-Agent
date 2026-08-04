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







        #
        # Direct operations
        #

        if not steps:



            if tool_name == "code":


                agent = self.agents.get(
                    "code"
                )


                if not agent:

                    return "Code agent not available."



                return self.process_tool_result(

                    agent.run(
                        message
                    ),

                    conversation

                )







            if tool_name == "chat":


                agent = self.agents.get(
                    "chat"
                )


                if not agent:

                    return "Chat agent not available."



                if conversation is not None:

                    agent.conversation = conversation



                return agent.chat(
                    message
                )








            agent = self.agents.get(
                "tool"
            )



            if not agent:

                return "Tool agent not available."



            return self.process_tool_result(

                agent.execute(
                    plan
                ),

                conversation

            )









        #
        # Single chat step
        #

        if (

            len(steps) == 1

            and

            steps[0].get("tool") == "chat"

        ):



            agent = self.agents.get(
                "chat"
            )



            if not agent:

                return "Chat agent not available."



            if conversation is not None:

                agent.conversation = conversation



            return agent.chat(
                message
            )









        #
        # Single code step
        #

        if (

            len(steps) == 1

            and

            steps[0].get("tool") == "code"

        ):



            agent = self.agents.get(
                "code"
            )



            if not agent:

                return "Code agent not available."



            return self.process_tool_result(

                agent.run(

                    steps[0].get(

                        "input",

                        message

                    )

                ),

                conversation

            )









        #
        # Multi tool workflow
        #

        agent = self.agents.get(
            "tool"
        )



        if not agent:

            return "Tool agent not available."



        result = agent.execute_steps(
            plan
        )



        return self.process_tool_result(

            result,

            conversation

        )













    def process_tool_result(
        self,
        result,
        conversation=None
    ):



        #
        # Multi-step results
        #

        if isinstance(result, list):


            outputs = []



            for item in result:



                if not isinstance(item, dict):

                    outputs.append(
                        str(item)
                    )

                    continue





                tool_result = item.get(
                    "result"
                )



                if tool_result is None:

                    continue



                outputs.append(

                    self.format_result(
                        tool_result
                    )

                )





            if outputs:

                return "\n\n".join(
                    outputs
                )



            return "İşlem tamamlandı."








        #
        # Single result
        #

        return self.format_result(
            result
        )













    def format_result(
        self,
        result
    ):



        #
        # Structured dictionary response
        #

        if isinstance(result, dict):


            #
            # File read result
            #

            if result.get(
                "action"
            ) == "read":



                return result.get(
                    "content",
                    ""
                )







            #
            # Successful operation
            #

            if result.get(
                "success"
            ):



                message = result.get(
                    "message"
                )



                if message:

                    return message



                return "İşlem başarıyla tamamlandı."









            #
            # Code analyzer result
            #

            if "analysis" in result:



                analysis = result.get(
                    "analysis"
                )



                if isinstance(
                    analysis,
                    dict
                ):



                    lines = []



                    for key,value in analysis.items():


                        title = key.replace(
                            "_",
                            " "
                        ).title()



                        lines.append(

                            f"{title}:\n{value}"

                        )



                    return "\n\n".join(
                        lines
                    )



                return str(
                    analysis
                )










            #
            # Code writer result
            #

            if "results" in result:


                return str(
                    result["results"]
                )










            #
            # Error
            #

            if result.get(
                "error"
            ):



                return str(
                    result["error"]
                )







            return str(
                result
            )









        #
        # String response
        #

        if isinstance(
            result,
            str
        ):



            if result.startswith(
                "File updated:"
            ):



                return (
                    "Dosya başarıyla güncellendi."
                )





            if result.startswith(
                "File created:"
            ):



                return (
                    "Dosya başarıyla oluşturuldu."
                )





            return result







        return str(
            result
        )