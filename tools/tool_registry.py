from app.core.logger import AppLogger



class ToolRegistry:


    def __init__(self):

        self.tools = {}

        self.logger = AppLogger()





    def register(
        self,
        name,
        tool
    ):


        self.tools[name] = tool


        self.logger.info(

            f"Tool registered: {name}"

        )








    def get(
        self,
        name
    ):


        return self.tools.get(
            name
        )








    def list_tools(
        self
    ):


        return list(
            self.tools.keys()
        )








    def execute(
        self,
        name,
        data
    ):


        tool = self.get(
            name
        )



        if tool is None:


            return f"Tool not found: {name}"





        if hasattr(
            tool,
            "execute"
        ):


            return tool.execute(
                data
            )





        return f"Tool {name} has no execute method."