class ToolRegistry:

    def __init__(self):

        self.tools = {}



    def register(
        self,
        name,
        tool
    ):

        if name in self.tools:

            raise ValueError(
                f"{name} is already registered."
            )


        self.tools[name] = tool



    def get(
        self,
        name
    ):

        return self.tools.get(name)



    def has(
        self,
        name
    ):

        return name in self.tools



    def list_tools(self):

        return list(
            self.tools.keys()
        )



    def remove(
        self,
        name
    ):

        if name in self.tools:

            del self.tools[name]