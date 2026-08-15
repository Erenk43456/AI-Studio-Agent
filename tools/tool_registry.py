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


        if not hasattr(tool, "execute"):

            self.logger.warning(
                f"Tool {name} has no execute method."
            )



        self.tools[name] = tool

        tool_description = getattr(
            tool,
            "description",
            "No description provided."
        )

        tool_purpose = getattr(
            tool,
            "purpose",
            "Unknown"
        )

        default_metadata = {

            "description":
                tool_description,

            "purpose": 
                tool_purpose,

            "safe":
                getattr(
                    tool,
                    "safe",
                    True
                ),

            "modifies_files":
                getattr(
                    tool,
                    "modifies_files",
                    False
                ),

            "requires_confirmation":
                getattr(
                    tool,
                    "requires_confirmation",
                    False
                ),

            "version":
                getattr(
                    tool,
                    "version",
                    "1.0"
                ),

        }

        if metadata:

            default_metadata.update(
                metadata
            )

        self.metadata[name] = (
            default_metadata
        )

        self.logger.info(
            f"Tool registered: {name}"
        )








    def unregister(
        self,
        name
    ):


        if name in self.tools:

            del self.tools[name]

            del self.metadata[name]


            self.logger.info(
                f"Tool removed: {name}"
            )


            return True



        return False







    def get(
        self,
        name
    ):


        return self.tools.get(
            name
        )









    def exists(
        self,
        name
    ):


        return name in self.tools









    def get_metadata(
        self,
        name
    ):


        return self.metadata.get(
            name,
            {}
        )









    def can_execute(
        self,
        name
    ):


        tool = self.get(
            name
        )


        if tool is None:

            return False



        return hasattr(
            tool,
            "execute"
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

            return {

                "success":False,

                "error":
                f"Tool not found: {name}"

            }




        if not hasattr(
            tool,
            "execute"
        ):


            return {

                "success":False,

                "error":
                f"Tool {name} has no execute method."

            }






        try:


            result = tool.execute(
                data
            )


            return {

                "success":True,

                "tool":
                name,

                "result":
                result

            }



        except Exception as error:


            self.logger.error(
                f"Tool execution error {name}: {error}"
            )


            return {

                "success":False,

                "tool":
                name,

                "error":
                str(error)

            }









    def get_tool_descriptions(
        self
    ):


        descriptions = []


        for name,data in self.metadata.items():


            descriptions.append({

                "name":
                name,


                "description":
                data.get(
                    "description",
                    ""
                ),


                "purpose":
                data.get(
                    "purpose",
                    ""
                ),


                "safe":
                data.get(
                    "safe",
                    True
                ),


                "modifies_files":
                data.get(
                    "modifies_files",
                    False
                ),


                "requires_confirmation":
                data.get(
                    "requires_confirmation",
                    False
                )

            })



        return descriptions









    def inspect_tool(
        self,
        name
    ):


        tool = self.get(
            name
        )


        if not tool:

            return None



        return {

            "name":
            name,


            "class":
            tool.__class__.__name__,


            "methods":
            [
                x
                for x in dir(tool)
                if not x.startswith("_")
            ],


            "has_execute":
            hasattr(
                tool,
                "execute"
            )


        }









    def list_tools(
        self
    ):


        return list(
            self.tools.keys()
        )