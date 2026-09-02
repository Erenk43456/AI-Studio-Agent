from dataclasses import dataclass, field
from typing import Any


@dataclass
class DecisionContract:
    """
    Contract representing the top-level routing decision from DecisionAgent.
    """
    system: str
    action: str = ""
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __getitem__(self, key: str) -> Any:
        if hasattr(self, key):
            return getattr(self, key)
        if key in self.metadata:
            return self.metadata[key]
        raise KeyError(key)

    def get(self, key: str, default: Any = None) -> Any:
        if hasattr(self, key):
            val = getattr(self, key)
            if val is not None and val != "":
                return val
            return default if default is not None else val
        return self.metadata.get(key, default)

    def __contains__(self, key: str) -> bool:
        return hasattr(self, key) or key in self.metadata
