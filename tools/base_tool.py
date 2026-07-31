class BaseTool:


    name = None

    description = None



    def execute(
        self,
        data
    ):

        raise NotImplementedError(
            "Tool must implement execute()"
        )