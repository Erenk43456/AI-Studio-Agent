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
    schema_version: int = 2
    generation_id: str = ""
    repository_fingerprint: str = ""
    repository_root: str = ""
    project: Dict[str, Any] = field(default_factory=dict)
    files: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    languages: Dict[str, int] = field(default_factory=dict)
    extensions: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    configuration_files: List[str] = field(default_factory=list)
    documentation_files: List[str] = field(default_factory=list)
    test_files: List[str] = field(default_factory=list)
    entry_points: List[str] = field(default_factory=list)
    source_boundaries: Dict[str, List[str]] = field(default_factory=dict)
    symbols: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    dependencies: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    architecture: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "generation_id": self.generation_id,
            "repository_fingerprint": self.repository_fingerprint,
            "repository_root": self.repository_root,
            "project": self.project,
            "generated_at": self.generated_at,
            "overview": self.overview,
            "files": self.files,
            "languages": self.languages,
            "extensions": self.extensions,
            "metadata": self.metadata,
            "configuration_files": self.configuration_files,
            "documentation_files": self.documentation_files,
            "test_files": self.test_files,
            "entry_points": self.entry_points,
            "source_boundaries": self.source_boundaries,
            "symbols": self.symbols,
            "dependencies": self.dependencies,
            "relationships": self.relationships,
            "architecture": self.architecture,
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
            indent=2,
        )
