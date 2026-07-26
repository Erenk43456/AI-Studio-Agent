from agents.base_agent import BaseAgent
from app.core.logger import AppLogger



class ToolAgent(BaseAgent):


    def __init__(
        self,
        registry,
        memory=None
    ):

        super().__init__(
            "Tool Agent",
            memory
        )


        self.registry = registry


        self.logger = AppLogger()





    def execute_steps(
        self,
        plan
    ):


        if not plan:


            self.logger.warning(
                "Empty multi-step plan received."
            )


            return "Invalid plan."





        steps = plan.get(
            "steps",
            []
        )



        # eski tek tool plan desteği

        if not steps:


            return self.execute(
                plan
            )





        results = []



        for index, step in enumerate(steps):


            self.logger.info(

                f"Executing step {index + 1}/{len(steps)}: {step.get('tool')}"

            )



            result = self.execute(
                step
            )



            results.append({

                "step": index + 1,

                "tool": step.get("tool"),

                "result": result

            })



        return results







    def execute(
        self,
        plan
    ):


        if not plan:


            self.logger.warning(
                "Empty tool plan received."
            )


            return "Invalid plan."




        tool_name = plan.get(
            "tool"
        )



        self.logger.info(

            f"Executing tool: {tool_name}"

        )





        try:



            if tool_name == "calculator":


                return self.run_calculator(
                    plan
                )






            if tool_name == "memory_save":


                tool = self.registry.get(
                    "memory"
                )


                if tool is None:

                    return "Memory tool not found."



                return tool.save_info(

                    plan.get("key"),

                    plan.get("value"),

                    plan.get(
                        "category",
                        "general"
                    )

                )







            if tool_name == "memory_get":


                tool = self.registry.get(
                    "memory"
                )


                if tool is None:

                    return "Memory tool not found."



                value = tool.get_info(

                    plan.get("key")

                )


                if value:

                    return value



                return "Information not found."







            if tool_name == "file":


                tool = self.registry.get(
                    "file"
                )


                if tool is None:

                    return "File tool not found."



                action = plan.get(

                    "action",

                    "create"

                )



                if action == "create":


                    return tool.create_file(

                        plan.get("filename"),

                        plan.get("content")

                    )



                if action == "write":


                    return tool.write_file(

                        plan.get("filename"),

                        plan.get("content")

                    )



                if action == "read":


                    return tool.read_file(

                        plan.get("filename")

                    )



                return "Invalid file operation."







            if tool_name == "formatter":


                tool = self.registry.get(
                    "formatter"
                )



                if tool is None:

                    return "Formatter tool not found."



                result = tool.format_code(

                    plan.get(

                        "code",

                        plan.get (

                            "input",

                            ""
                        )

                    )

                )



                if result["success"]:


                    return result["code"]



                return result["message"]







            if tool_name == "code_repair":


                tool = self.registry.get(
                    "code_repair"
                )


                if tool is None:

                    return "Code repair tool not found."



                result = tool.repair_code(

                    plan.get(

                        "code",

                        plan.get (

                            "input",

                            ""
                        )

                    )

                )



                if result["success"]:

                    return result["code"]



                return result["message"]







            if tool_name == "code_analyzer":


                tool = self.registry.get(
                    "code_analyzer"
                )



                if tool is None:

                    return "Code analyzer tool not found."



                result = tool.analyze_code(

                    plan.get(

                        "code",

                        plan.get (

                            "input",

                            ""
                        )

                    )

                )



                if result["success"]:

                    return result["analysis"]



                return result["message"]








            if tool_name == "chat":


                return plan.get(

                    "message",

                    plan.get(

                        "input",

                        "How can I help you?"

                    )

                )







            self.logger.warning(

                f"Unknown tool requested: {tool_name}"

            )


            return "Unknown tool."








        except Exception as error:


            self.logger.error(

                f"Tool execution error: {error}"

            )


            return f"Tool error: {error}"









    def run_calculator(
        self,
        plan
    ):



        tool = self.registry.get(

            "calculator"

        )



        if tool is None:


            return "Calculator not found."





        numbers = plan.get(

            "numbers",

            []

        )



        if len(numbers) < 2:


            return "Two numbers required."





        a = float(

            numbers[0]

        )


        b = float(

            numbers[1]

        )



        operation = plan.get(

            "operation"

        )





        if operation == "add":


            return tool.add(

                a,

                b

            )





        if operation == "subtract":


            return tool.subtract(

                a,

                b

            )





        if operation == "multiply":


            return tool.multiply(

                a,

                b

            )





        if operation == "divide":


            return tool.divide(

                a,

                b

            )





        return "Unsupported operation."