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





    def execute(
        self,
        plan
    ):


        if not plan:


            self.logger.warning(
                "Empty tool plan received."
            )


            return "Geçersiz plan."





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


                    return "Memory tool bulunamadı."



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


                    return "Memory tool bulunamadı."



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



                if tool is None:


                    return "File tool bulunamadı."



                return tool.create_file(

                    plan.get("filename"),

                    plan.get("content")

                )








            if tool_name == "chat":


                return plan.get(

                    "message",

                    "Size nasıl yardımcı olabilirim?"

                )







            self.logger.warning(

                f"Unknown tool requested: {tool_name}"

            )


            return "Bilinmeyen araç."







        except Exception as error:


            self.logger.error(

                f"Tool execution error: {error}"

            )


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