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



        #
        # Decision Phase
        #

        decision_agent = self.agents.get(
            "decision"
        )



        if decision_agent:


            decision = decision_agent.process(
                message
            )


        else:


            decision = {
                "agent": "chat"
            }

        if isinstance(decision, dict):
        
            decision_type = decision.get(
                "agent",
                "chat"
            )
        
        else:
        
            decision_type = decision



        self.logger.info(
            f"Decision selected: {decision}"
        )



        print(
            "\n===== DECISION ====="
        )

        print(
            decision
        )

        print(
            "====================\n"
        )







        #
        # CHAT
        #

        if decision_type == "chat":


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
        # MEMORY
        #

        if decision_type == "memory":

            agent = self.agents.get(
                "memory"
            )


            if not agent:

                return "Memory agent not available."


            if not isinstance(
                decision,
                dict
            ):

                return "Invalid memory request."



            action = decision.get(
                "action"
            )


            if action == "save":

                return agent.save(
                    message
                )


            if action == "get":

                return agent.get(
                    message
                )


            return "Unknown memory action."

            if action == "save":

                return agent.save(
                    message
                )


            if action == "get":

                return agent.get(
                    message
                )


            return "Unknown memory action."






        #
        # TOOL
        #

        if decision_type == "tool":



            agent = self.agents.get(
                "tool"
            )



            if not agent:

                return "Tool agent not available."



            result = agent.execute(
                {
                    "input": message,
                    "tool": decision.get("tool")
                }
            )



            return self.process_tool_result(
                result,
                conversation
            )









        #
        # CODE / COMPLEX TASK
        #

        if decision_type == "code":



            #
            # Planner creates workflow
            #

            plan = self.planner.create_plan(
                message
            )



            print(
                "\n===== GENERATED PLAN ====="
            )

            print(
                plan
            )

            print(
                "==========================\n"
            )



            if not plan:


                return (
                    "Planner failed to create a plan."
                )





            steps = plan.get(
                "steps",
                []
            )



            #
            # Direct code execution
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



                result = agent.run(

                    steps[0].get(

                        "input",

                        message

                    )

                )



                return self.process_tool_result(
                    result,
                    conversation
                )









            #
            # Multi step workflow
            #

            tool_agent = self.agents.get(
                "tool"
            )



            if tool_agent:


                result = tool_agent.execute_steps(
                    plan
                )


                return self.process_tool_result(
                    result,
                    conversation
                )



            return "Workflow executor not available."









        #
        # Planner fallback
        #

        plan = self.planner.create_plan(
            message
        )



        if not plan:

            return "Planner failed."



        agent = self.agents.get(
            "tool"
        )


        if agent:

            result = agent.execute_steps(
                plan
            )


            return self.process_tool_result(
                result,
                conversation
            )



        return "No suitable agent."











    def process_tool_result(
        self,
        result,
        conversation=None
    ):



        if isinstance(
            result,
            list
        ):


            outputs = []



            for item in result:



                if not isinstance(
                    item,
                    dict
                ):


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









        return self.format_result(
            result
        )









    def format_result(
        self,
        result
    ):



        if isinstance(
            result,
            dict
        ):



            if result.get(
                "action"
            ) == "read":


                return result.get(
                    "content",
                    ""
                )





            if result.get(
                "success"
            ):


                message = result.get(
                    "message"
                )



                if message:

                    return message



                return "İşlem başarıyla tamamlandı."







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







            if "results" in result:


                return str(
                    result["results"]
                )







            if result.get(
                "error"
            ):


                return str(
                    result["error"]
                )



            return str(
                result
            )







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

            #
        # CODE / COMPLEX TASK
        #

        if decision_type == "code":


            #
            # Planner creates workflow
            #

            plan = self.planner.create_plan(
                message
            )


            print(
                "\n===== GENERATED PLAN ====="
            )

            print(
                plan
            )

            print(
                "==========================\n"
            )


            if not plan:

                return (
                    "Planner failed to create a plan."
                )



            steps = plan.get(
                "steps",
                []
            )



            #
            # Direct code execution
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


                result = agent.run(

                    steps[0].get(

                        "input",

                        message

                    )

                )


                return self.process_tool_result(
                    result,
                    conversation
                )




            #
            # Multi step workflow
            #

            tool_agent = self.agents.get(
                "tool"
            )


            if tool_agent:


                result = tool_agent.execute_steps(
                    plan
                )


                return self.process_tool_result(
                    result,
                    conversation
                )


            return "Workflow executor not available."





        #
        # Planner fallback
        #

        plan = self.planner.create_plan(
            message
        )


        if not plan:

            return "Planner failed."


        agent = self.agents.get(
            "tool"
        )


        if agent:

            result = agent.execute_steps(
                plan
            )


            return self.process_tool_result(
                result,
                conversation
            )


        return "No suitable agent."






    def process_tool_result(
        self,
        result,
        conversation=None
    ):


        if isinstance(
            result,
            list
        ):


            outputs = []


            for item in result:


                if not isinstance(
                    item,
                    dict
                ):

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


        return self.format_result(
            result
        )





    def format_result(
        self,
        result
    ):


        if isinstance(
            result,
            dict
        ):


            if result.get(
                "action"
            ) == "read":

                return result.get(
                    "content",
                    ""
                )


            if result.get(
                "success"
            ):

                message = result.get(
                    "message"
                )

                if message:

                    return message

                return "İşlem başarıyla tamamlandı."


            if "analysis" in result:

                analysis = result.get(
                    "analysis"
                )

                if isinstance(
                    analysis,
                    dict
                ):

                    lines = []

                    for key, value in analysis.items():

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


            if "results" in result:

                return str(
                    result["results"]
                )


            if result.get(
                "error"
            ):

                return str(
                    result["error"]
                )

            return str(
                result
            )


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