"""Structured internal representation for repository analysis results.

Separates analysis data from human-readable formatting so future
agents (e.g. CodeReviewAgent) can consume the data directly as a
plain dictionary or JSON string.
"""

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class RepositoryAnalysis:
    """Structured result of a repository analysis.

    Each field holds raw analysis data (no rendering). Convert to a
    JSON-friendly dictionary with ``to_dict()``.
    """

    generated_at: str
    overview: Dict[str, Any] = field(default_factory=dict)
    module_roles: Dict[str, str] = field(default_factory=dict)
    definitions: Dict[str, List[str]] = field(default_factory=dict)
    tools: List[Dict[str, Any]] = field(default_factory=list)
    registry_names: List[str] = field(default_factory=list)
    wiring_checks: List[Dict[str, Any]] = field(default_factory=list)
    issues: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "overview": self.overview,
            "module_roles": self.module_roles,
            "definitions": self.definitions,
            "tools": self.tools,
            "registry_names": self.registry_names,
            "wiring_checks": self.wiring_checks,
            "issues": self.issues,
        }

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            indent=2
        )
