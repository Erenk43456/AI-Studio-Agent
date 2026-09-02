from abc import ABC, abstractmethod


class AgentContract(ABC):
    """
    Contract interface that all agents in AI-Studio must satisfy.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the agent."""
        pass

    @abstractmethod
    def run(self, task: str):
        """Execute the given task string."""
        pass

    @abstractmethod
    def remember(self, key: str, value: str):
        """Save a key-value pair to agent memory."""
        pass

    @abstractmethod
    def recall(self):
        """Recall stored memory for this agent."""
        pass
