class BaseAgent:


    def __init__(
        self,
        name,
        memory=None
    ):

        self.name = name

        self.memory = memory



    def remember(
        self,
        key,
        value
    ):

        if self.memory:

            self.memory.save(
                f"{self.name}:{key}",
                value
            )



    def recall(
        self
    ):

        if self.memory:

            return self.memory.recall()

        return None



    def run(
        self,
        task
    ):

        raise NotImplementedError(
            "Agent must implement run()"
        )