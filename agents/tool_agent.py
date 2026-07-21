from agents.base_agent import BaseAgent


class ToolAgent(BaseAgent):

    def __init__(self, registry):
        super().__init__("Tool Agent")

        self.registry = registry


    def execute(self, plan):

        if not plan:
            return "Geçersiz plan."


        tool_name = plan.get("tool")


        try:

            # Calculator
            if tool_name == "calculator":

                tool = self.registry.get(
                    "calculator"
                )

                if tool is None:
                    return "Calculator aracı bulunamadı."


                numbers = plan.get(
                    "numbers",
                    []
                )


                if len(numbers) < 2:
                    return "Hesaplama için iki sayı gerekli."


                a = float(numbers[0])
                b = float(numbers[1])


                operation = plan.get(
                    "operation"
                )


                if operation == "add":
                    return tool.add(a, b)


                if operation == "multiply":
                    return tool.multiply(a, b)


                if operation == "subtract":
                    return tool.subtract(a, b)


                if operation == "divide":

                    if b == 0:
                        return "Sıfıra bölme yapılamaz."

                    return tool.divide(a, b)



                return "Bilinmeyen işlem."


            # Memory kayıt
            if tool_name == "memory_save":

                memory_tool = self.registry.get(
                    "memory"
                )


                return memory_tool.save_info(
                    plan.get("key"),
                    plan.get("value")
                )



            # Memory okuma
            if tool_name == "memory_get":

                memory_tool = self.registry.get(
                    "memory"
                )


                value = memory_tool.get_info(
                    plan.get("key")
                )


                if value:
                    return value


                return "Bilgi bulunamadı."



            # Dosya
            if tool_name == "file":

                file_tool = self.registry.get(
                    "file"
                )


                return file_tool.create_file(
                    plan.get("filename"),
                    plan.get("content")
                )


            return "Çalıştırılacak araç bulunamadı."


        except Exception as error:

            return f"Araç çalıştırma hatası: {error}"