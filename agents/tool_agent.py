from agents.base_agent import BaseAgent


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



    def execute(
        self,
        plan
    ):

        if not plan:
            return "Invalid plan."


        tool_name = plan.get(
            "tool"
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

                return tool.save_info(
                    plan.get("key"),
                    plan.get("value")
                )



            if tool_name == "memory_get":

                tool = self.registry.get(
                    "memory"
                )


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

                return tool.create_file(
                    plan.get("filename"),
                    plan.get("content")
                )



            if tool_name == "chat":

                return plan.get(
                    "message",
                    "How can I help you?"
                )



            return "Unknown tool."



        except Exception as error:

            return f"Tool error: {error}"




    def run_calculator(
        self,
        plan
    ):

        tool = self.registry.get(
            "calculator"
        )


        if tool is None:
            return "Calculator tool not found."


        numbers = plan.get(
            "numbers",
            []
        )


        if len(numbers) < 2:
            return "Two numbers are required."


        a = float(numbers[0])
        b = float(numbers[1])


        operation = plan.get(
            "operation"
        )


        if operation == "add":
            return tool.add(a,b)


        if operation == "multiply":
            return tool.multiply(a,b)


        return "Unsupported operation."