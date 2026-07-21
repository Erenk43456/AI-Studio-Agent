from agents.base_agent import BaseAgent


class ToolAgent(BaseAgent):

    def __init__(self, registry):
        super().__init__("Tool Agent")
        self.registry = registry


    def execute(self, plan):

        tool_name = plan.get("tool")


        if tool_name == "calculator":

            tool = self.registry.get("calculator")

            numbers = plan.get("numbers")

            a = int(numbers[0])
            b = int(numbers[1])

            operation = plan.get("operation")


            if operation == "add":
                return tool.add(a, b)


            if operation == "multiply":
                return tool.multiply(a, b)



        if tool_name == "memory_save":

            memory_tool = self.registry.get("memory")

            return memory_tool.save_info(
                plan.get("key"),
                plan.get("value")
            )



        if tool_name == "memory_get":

            memory_tool = self.registry.get("memory")

            value = memory_tool.get_info(
                plan.get("key")
            )

            if value:
                return value

            return "Bilgi bulunamadı."



        if tool_name == "file":

            file_tool = self.registry.get("file")

            return file_tool.create_file(
                plan.get("filename"),
                plan.get("content")
            )


        return "Çalıştırılacak araç bulunamadı."