from app.core.logger import AppLogger



class ToolRegistry:


    def __init__(self):

        self.tools = {}

        self.metadata = {}

        self.logger = AppLogger()





    def register(
        self,
        name,
        tool,
        metadata=None
    ):


        self.tools[name] = tool


        self.metadata[name] = metadata or {

            "description": "No description provided.",

            "purpose": "Unknown",

            "safe": True,

            "modifies_files": False

        }


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









    def get_metadata(
        self,
        name
    ):


        return self.metadata.get(

            name

        )









    def get_tool_descriptions(
        self
    ):


        descriptions = []


        for name, data in self.metadata.items():


            descriptions.append({

                "name": name,

                "description": data.get(

                    "description",

                    ""

                ),

                "purpose": data.get(

                    "purpose",

                    ""

                ),

                "safe": data.get(

                    "safe",

                    True

                ),

                "modifies_files": data.get(

                    "modifies_files",

                    False

                )

            })


        return descriptions









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