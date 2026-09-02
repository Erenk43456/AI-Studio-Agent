from contracts.agent_contract import AgentContract


class BaseAgent(AgentContract):

    def __init__(
        self,
        name,
        memory=None
    ):
        self._name = name
        self.memory = memory

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

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