from dataclasses import dataclass, field
from typing import Any


@dataclass
class PlannerStep:
    """
    Contract representing a single step within an execution plan.
    Supports both typed attribute access (step.tool) and dict-like access (step.get("tool")).
    """
    tool: str
    action: str
    input: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)

    def __getitem__(self, key: str) -> Any:
        if hasattr(self, key):
            return getattr(self, key)
        if key in self.parameters:
            return self.parameters[key]
        if key in self.context:
            return self.context[key]
        raise KeyError(key)

    def __setitem__(self, key: str, value: Any) -> None:
        if hasattr(self, key) and key not in ("parameters", "context"):
            setattr(self, key, value)
        else:
            self.parameters[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        if hasattr(self, key):
            val = getattr(self, key)
            if val is not None and val != "":
                return val
            return default if default is not None and (val == "" or val is None) else val
        if key in self.parameters:
            return self.parameters[key]
        if key in self.context:
            return self.context[key]
        return default

    def __contains__(self, key: str) -> bool:
        return hasattr(self, key) or key in self.parameters or key in self.context

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, PlannerStep):
            return (
                self.tool == other.tool
                and self.action == other.action
                and self.input == other.input
                and self.parameters == other.parameters
                and self.context == other.context
            )
        if isinstance(other, dict):
            tool = other.get("tool")
            action = other.get("action")
            inp = other.get("input", "")
            return (
                self.tool == tool
                and self.action == action
                and (self.input == inp or (not self.input and not inp))
            )
        return False


@dataclass
class PlannerContract:
    """
    Contract representing the complete execution plan created by PlannerAgent.
    Supports both typed attribute access (plan.steps) and dict-like access (plan.get("steps")).
    """
    steps: list[PlannerStep]
    user_message: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __getitem__(self, key: str) -> Any:
        if hasattr(self, key):
            return getattr(self, key)
        if key in self.metadata:
            return self.metadata[key]
        raise KeyError(key)

    def __setitem__(self, key: str, value: Any) -> None:
        if hasattr(self, key) and key != "metadata":
            setattr(self, key, value)
        else:
            self.metadata[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        if hasattr(self, key):
            val = getattr(self, key)
            if val is not None:
                return val
            return default
        return self.metadata.get(key, default)

    def __contains__(self, key: str) -> bool:
        return hasattr(self, key) or key in self.metadata

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, PlannerContract):
            return (
                self.steps == other.steps
                and self.user_message == other.user_message
            )
        if isinstance(other, dict):
            other_steps = other.get("steps", [])
            if len(self.steps) != len(other_steps):
                return False
            return all(s == o for s, o in zip(self.steps, other_steps))
        return False
