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
            return "Geçersiz plan."


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


                return "Bilgi bulunamadı."



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
                    "Size nasıl yardımcı olabilirim?"
                )



            return "Bilinmeyen araç."



        except Exception as error:

            return f"Araç hatası: {error}"





    def run_calculator(
        self,
        plan
    ):


        tool = self.registry.get(
            "calculator"
        )


        if tool is None:

            return "Calculator bulunamadı."



        numbers = plan.get(
            "numbers",
            []
        )


        if len(numbers) < 2:

            return "İki sayı gerekli."



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



        return "Desteklenmeyen işlem."