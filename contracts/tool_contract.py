from abc import ABC, abstractmethod


class ToolContract(ABC):
    """
    Contract interface that all tools in AI-Studio must satisfy.
    """

    name = None
    description = None

    @abstractmethod
    def execute(self, data):
        """Execute the tool with the given data/input."""
        pass
