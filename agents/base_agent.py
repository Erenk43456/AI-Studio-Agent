from memory.memory import Memory


class BaseAgent:

    def __init__(
        self,
        name,
        memory=None
    ):

        self.name = name
        self.memory = memory or Memory()



    def think(
        self,
        task
    ):

        self.memory.save(
            "last_thought",
            task
        )

        return f"{self.name} is thinking: {task}"



    def remember(self):

        return self.memory.recall()



    def act(
        self,
        task
    ):

        self.memory.save(
            "last_action",
            task
        )

        return f"{self.name} is executing: {task}"