from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolResultContract:
    """
    Contract representing the standardized output of a tool execution.
    Supports both typed attribute access (result.success) and dict-like access (result.get("success")),
    as well as equality comparisons against strings, dicts, or other ToolResultContracts.
    """
    success: bool
    message: str = ""
    error: Any = None
    data: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __getitem__(self, key: str) -> Any:
        if hasattr(self, key):
            return getattr(self, key)
        if key in self.metadata:
            return self.metadata[key]
        if isinstance(self.data, dict) and key in self.data:
            return self.data[key]
        raise KeyError(key)

    def get(self, key: str, default: Any = None) -> Any:
        if hasattr(self, key):
            val = getattr(self, key)
            if val is not None and val != "":
                return val
            return default if default is not None and (val == "" or val is None) else val
        if key in self.metadata:
            return self.metadata[key]
        if isinstance(self.data, dict) and key in self.data:
            return self.data.get(key, default)
        return default

    def __contains__(self, key: str) -> bool:
        return (
            hasattr(self, key)
            or key in self.metadata
            or (isinstance(self.data, dict) and key in self.data)
        )

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ToolResultContract):
            return (
                self.success == other.success
                and self.message == other.message
                and self.error == other.error
                and self.data == other.data
            )
        if isinstance(other, str):
            return self.data == other or self.message == other
        if isinstance(other, bool):
            return self.success == other
        if isinstance(other, dict):
            # Check if matching dict format
            match = True
            for k, v in other.items():
                if self.get(k) != v:
                    match = False
                    break
            return match
        return False
