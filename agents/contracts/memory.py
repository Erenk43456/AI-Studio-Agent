from dataclasses import dataclass
from typing import Any


@dataclass
class MemoryContract:
    """
    Contract representing a memory operation (get, save, search, etc.).
    """
    action: str
    key: str
    value: Any = None
    category: str = "general"
