from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolStepContract:
    """
    Contract representing the invocation request sent to ToolAgent / Tool.
    Supports both typed attribute access and dict-like access, plus dict equality.
    """
    tool: str
    action: str = "execute"
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
        if isinstance(other, ToolStepContract):
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
                and (self.action == action or not action)
                and (self.input == inp or (not self.input and not inp))
            )
        return False
