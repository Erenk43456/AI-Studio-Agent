from abc import ABC, abstractmethod


class PlannerContract(ABC):
    """
    Contract interface that all planners / plan creators in AI-Studio must satisfy.
    """

    @abstractmethod
    def create_plan(self, task: str) -> dict:
        """Create an execution plan dictionary for the given task."""
        pass
