"""Resolve bounded development context from the persisted repository snapshot."""

from pathlib import Path


class RepositoryContextResolver:
    """Read-only resolver for ProjectMemory repository knowledge."""

    def __init__(self, project_memory):
        self.project_memory = project_memory

    def resolve(self, target_files, target_symbols=None, max_files=12):
        targets = self._normalize_paths(target_files)
        target_symbols = self._normalize_symbols(target_symbols)
        limit = self._normalize_limit(max_files, len(targets))

        files = self._read_mapping("get_all_files", {})
        symbols = self._read_mapping("get_symbols", {})
        dependencies = self._read_mapping("get_dependencies", {})
        relationships = self._read_relationships()

        selected = set(targets)
        candidates = {}

        for edge in relationships:
            source = self._normalize_path(edge.get("source"))
            target = self._normalize_path(edge.get("target"))
            kind = str(edge.get("kind") or edge.get("relationship") or "related")

            for candidate, other, direction in (
                (source, target, "outgoing"),
                (target, source, "incoming"),
            ):
                if candidate not in targets or not other or other in selected:
                    continue
                self._add_candidate(
                    candidates,
                    other,
                    kind,
                    direction,
                    edge.get("score", 0),
                )

        for source, source_dependencies in dependencies.items():
            source_path = self._normalize_path(source)
            if not isinstance(source_dependencies, list):
                continue
            for dependency in source_dependencies:
                if not isinstance(dependency, dict):
                    continue
                target_path = self._normalize_path(
                    dependency.get("target") or dependency.get("file")
                )
                if source_path in targets and target_path:
                    self._add_candidate(
                        candidates,
                        target_path,
                        dependency.get("kind", "dependency"),
                        "outgoing",
                        0,
                    )
                elif target_path in targets and source_path:
                    self._add_candidate(
                        candidates,
                        source_path,
                        dependency.get("kind", "dependency"),
                        "incoming",
                        0,
                    )

        ordered_candidates = sorted(
            candidates.items(),
            key=lambda item: (-item[1]["score"], item[0]),
        )
        selected_related = ordered_candidates[: max(0, limit - len(selected))]
        selected.update(path for path, _ in selected_related)

        selected_files = [path for path in targets]
        selected_files.extend(path for path, _ in selected_related)

        return {
            "targets": targets,
            "target_files": {path: files[path] for path in targets if path in files},
            "related_files": [
                {
                    "file": path,
                    "reason": details["reason"],
                    "relationship": details["relationship"],
                    "score": details["score"],
                    "info": files.get(path),
                }
                for path, details in selected_related
            ],
            "symbols": self._select_symbols(symbols, selected_files, target_symbols),
            "dependencies": self._select_dependencies(dependencies, selected_files),
            "relationships": [
                edge
                for edge in relationships
                if self._normalize_path(edge.get("source")) in selected
                or self._normalize_path(edge.get("target")) in selected
            ],
            "metadata": {
                "total_candidates": len(candidates),
                "selected_files": len(selected_files),
                "truncated": len(ordered_candidates) > len(selected_related),
            },
        }

    def _read_mapping(self, method_name, default):
        method = getattr(self.project_memory, method_name, None)
        if method is None:
            return default
        try:
            value = method()
        except Exception:
            return default
        return value if isinstance(value, dict) else default

    def _read_relationships(self):
        method = getattr(self.project_memory, "get_relationships", None)
        if method is None:
            return []
        try:
            value = method()
        except Exception:
            return []
        if isinstance(value, dict):
            value = value.get("edges", [])
        if not isinstance(value, list):
            return []
        return [edge for edge in value if isinstance(edge, dict)]

    @staticmethod
    def _normalize_paths(paths):
        if isinstance(paths, (str, Path)):
            paths = [paths]
        if not isinstance(paths, (list, tuple, set)):
            return []
        result = []
        for path in paths:
            normalized = RepositoryContextResolver._normalize_path(path)
            if normalized and normalized not in result:
                result.append(normalized)
        return result

    @staticmethod
    def _normalize_path(path):
        if path is None:
            return ""
        return str(path).replace("\\", "/").lstrip("./")

    @staticmethod
    def _normalize_symbols(symbols):
        if symbols is None:
            return set()
        if isinstance(symbols, str):
            symbols = [symbols]
        return {str(symbol) for symbol in symbols if symbol}

    @staticmethod
    def _normalize_limit(max_files, target_count):
        try:
            limit = int(max_files)
        except (TypeError, ValueError):
            limit = 12
        return max(target_count, limit)

    @staticmethod
    def _add_candidate(candidates, path, relationship, direction, score):
        if not path:
            return
        try:
            numeric_score = float(score)
        except (TypeError, ValueError):
            numeric_score = 0
        details = candidates.setdefault(
            path,
            {
                "score": 0,
                "relationships": [],
                "directions": [],
            },
        )
        details["score"] += 10 + numeric_score
        relation = f"{direction}:{relationship}"
        if relation not in details["relationships"]:
            details["relationships"].append(relation)
        if direction not in details["directions"]:
            details["directions"].append(direction)
        details["relationship"] = ",".join(details["relationships"])
        details["reason"] = " and ".join(
            f"{direction} {relationship}" for direction in details["directions"]
        )

    @staticmethod
    def _select_symbols(symbols, selected_files, target_symbols):
        result = {}
        for path in selected_files:
            values = symbols.get(path, [])
            if not isinstance(values, list):
                continue
            if target_symbols:
                values = [
                    value
                    for value in values
                    if isinstance(value, dict)
                    and (
                        value.get("name") in target_symbols
                        or value.get("id") in target_symbols
                    )
                ]
            if values:
                result[path] = sorted(
                    values,
                    key=lambda value: (
                        value.get("line") or 0,
                        value.get("id", ""),
                    ),
                )
        return result

    @staticmethod
    def _select_dependencies(dependencies, selected_files):
        return {
            path: dependencies[path]
            for path in selected_files
            if path in dependencies and isinstance(dependencies[path], list)
        }
