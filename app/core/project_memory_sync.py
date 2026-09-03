from copy import deepcopy
from datetime import datetime
import hashlib
import json
from pathlib import Path

from app.core.logger import AppLogger
from tools.python_analyzer import PythonAnalyzer
from tools.repository_indexer import RepositoryIndexer


class ProjectMemorySync:

    def __init__(self, repository_analyzer, project_memory, workspace):
        self.repository_analyzer = repository_analyzer
        self.project_memory = project_memory
        self.workspace = Path(workspace)
        self.logger = AppLogger()
        self.indexer = RepositoryIndexer()
        self.python_analyzer = PythonAnalyzer()

    def sync(self, changed_files):
        if not changed_files:
            return None

        normalized = self._normalize_changed_files(changed_files)
        if normalized is None:
            return self._run_full_rescan(
                changed_files,
                "full_rescan_fallback",
            )

        if not self._snapshot_is_valid():
            return self._run_full_rescan(
                normalized,
                "full_rescan_fallback",
            )

        try:
            merged = self._build_incremental_snapshot(normalized)
            if merged is None:
                raise ValueError("Incremental snapshot could not be built.")

            if not self.project_memory.sync_repository_analysis(merged):
                raise RuntimeError("Incremental snapshot persistence failed.")

            self.last_changed_files = normalized
            self.last_sync_mode = "incremental"
            return merged

        except Exception as error:
            self.logger.error(f"Incremental repository sync failed: {error}")
            self._mark_failed(normalized, str(error))
            return self._run_full_rescan(
                normalized,
                "full_rescan_fallback",
            )

    def initialize(self):
        has_valid_snapshot = getattr(
            self.project_memory,
            "has_valid_repository_snapshot",
            None,
        )

        if not has_valid_snapshot:
            return None

        if has_valid_snapshot():
            return self.project_memory.get_analysis_state()

        set_state = getattr(
            self.project_memory,
            "set_analysis_state",
            None,
        )

        if set_state:
            set_state(
                {
                    "status": "indexing",
                    "repository_root": str(self.workspace.resolve()),
                }
            )

        return self._run_full_rescan(
            [],
            "initial_full_scan",
        )

    def _run_full_rescan(self, changed_files, mode):
        self.last_changed_files = list(changed_files)
        self.last_sync_mode = mode

        try:
            result = self.repository_analyzer.analyze(self.workspace)

            if result is None or isinstance(result, str):
                self._mark_failed(
                    changed_files,
                    "Repository analysis did not produce structured data.",
                )
                return None

            if not self.project_memory.sync_repository_analysis(result):
                self._mark_failed(
                    changed_files,
                    "Repository analysis persistence failed.",
                )
                return None

            return result

        except Exception as error:
            self.logger.error(f"Project memory sync failed: {error}")
            self._mark_failed(changed_files, str(error))
            return None

    def _snapshot_is_valid(self):
        validator = getattr(
            self.project_memory,
            "has_valid_repository_snapshot",
            None,
        )
        if not callable(validator):
            return False
        try:
            return bool(validator())
        except Exception:
            return False

    def _normalize_changed_files(self, changed_files):
        try:
            normalized = set()
            workspace = self.workspace.resolve()
            for changed_file in changed_files:
                path = Path(changed_file)
                if not path.is_absolute():
                    path = workspace / path
                resolved = path.resolve()
                relative = resolved.relative_to(workspace).as_posix()
                normalized.add(relative)
            return sorted(normalized)
        except (OSError, TypeError, ValueError):
            return None

    def _build_incremental_snapshot(self, changed_files):
        analysis = self._load_current_snapshot()
        if analysis is None:
            return None

        files = analysis["files"]
        symbols = analysis["symbols"]
        dependencies = analysis["dependencies"]
        definitions = analysis["definitions"]
        module_roles = analysis["module_roles"]

        deleted_files = set()

        for relative in changed_files:
            path = self.workspace / relative

            if not path.exists():
                files.pop(relative, None)
                symbols.pop(relative, None)
                dependencies.pop(relative, None)
                definitions.pop(relative, None)
                module_roles.pop(relative, None)
                deleted_files.add(relative)
                continue

            metadata = self.indexer.file_metadata(path, relative)
            files[relative] = metadata

            if metadata.get("language") == "python":
                result = self.python_analyzer.analyze_file(path, self.workspace)
                if not self._valid_python_result(result):
                    return None
                if result["symbols"]:
                    symbols[relative] = result["symbols"]
                else:
                    symbols.pop(relative, None)
                if result["dependencies"]:
                    dependencies[relative] = result["dependencies"]
                else:
                    dependencies.pop(relative, None)
                if result["definitions"]:
                    definitions[relative] = result["definitions"]
                else:
                    definitions.pop(relative, None)
            else:
                symbols.pop(relative, None)
                dependencies.pop(relative, None)
                definitions.pop(relative, None)

        analysis["files"] = dict(sorted(files.items()))
        analysis["symbols"] = self._sorted_mapping(symbols)
        analysis["dependencies"] = self._sorted_mapping(dependencies)
        analysis["definitions"] = self._sorted_mapping(definitions)
        analysis["module_roles"] = self._sorted_mapping(module_roles)
        analysis["relationships"] = deepcopy(analysis["relationships"])

        if deleted_files:
            normalized_deleted_files = {
                self._normalize_relative(path) 
                for path in deleted_files
            }

            analysis["relationships"] = [
                edge
                for edge in analysis["relationships"]
                if self._normalize_relative(edge.get("source")) 
                not in normalized_deleted_files
                and self._normalize_relative(edge.get("target"))
                not in normalized_deleted_files
            ]

        self._recompute_snapshot_fields(analysis)
        analysis["sync_mode"] = "incremental"
        return analysis

    def _load_current_snapshot(self):
        if not self._snapshot_is_valid():
            return None

        architecture = self._read_mapping("get_architecture", {})
        analysis = architecture.get("repository_analysis")
        if not isinstance(analysis, dict):
            return None

        files = self._read_mapping("get_all_files", {})
        symbols = self._read_mapping("get_symbols", {})
        dependencies = self._read_mapping("get_dependencies", {})
        relationships = self._read_relationships()

        definitions = {}
        module_roles = {}
        for path, info in files.items():
            normalized = self._normalize_relative(path)
            if not normalized or not isinstance(info, dict):
                continue
            if info.get("definitions"):
                definitions[normalized] = deepcopy(info["definitions"])
            if info.get("role"):
                module_roles[normalized] = info["role"]

        snapshot = deepcopy(analysis)
        snapshot["files"] = {
            self._normalize_relative(path): deepcopy(info)
            for path, info in files.items()
            if self._normalize_relative(path)
        }
        snapshot["symbols"] = deepcopy(symbols)
        snapshot["dependencies"] = deepcopy(dependencies)
        snapshot["relationships"] = relationships
        snapshot["definitions"] = definitions
        snapshot["module_roles"] = module_roles
        return snapshot

    def _recompute_snapshot_fields(self, analysis):
        files = analysis["files"]
        languages = {}
        extensions = {}
        total_bytes = 0
        total_lines = 0
        for path, metadata in sorted(files.items()):
            language = metadata.get("language", "unknown")
            extension = metadata.get("extension") or "[no extension]"
            languages[language] = languages.get(language, 0) + 1
            extensions[extension] = extensions.get(extension, 0) + 1
            total_bytes += metadata.get("size_bytes", 0) or 0
            total_lines += metadata.get("line_count", 0) or 0

        analysis["languages"] = dict(sorted(languages.items()))
        analysis["extensions"] = dict(sorted(extensions.items()))
        analysis["metadata"] = {
            **analysis.get("metadata", {}),
            "total_files": len(files),
            "total_bytes": total_bytes,
            "total_lines": total_lines,
        }
        overview = dict(analysis.get("overview", {}))
        overview.update(
            {
                "total_files": len(files),
                "total_bytes": total_bytes,
                "total_lines": total_lines,
                "python_files": languages.get("python", 0),
                "languages": analysis["languages"],
                "extensions": analysis["extensions"],
            }
        )
        analysis["overview"] = overview
        fingerprint = self._fingerprint(files)
        analysis["repository_fingerprint"] = fingerprint
        analysis["generation_id"] = hashlib.sha256(
            f"repository-analysis-v2:{fingerprint}".encode()
        ).hexdigest()
        analysis["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _fingerprint(files):
        payload = json.dumps(
            [(path, files[path].get("content_hash", "")) for path in sorted(files)],
            ensure_ascii=True,
            separators=(",", ":"),
        )
        return "sha256:" + hashlib.sha256(payload.encode()).hexdigest()

    def _read_mapping(self, method_name, default):
        method = getattr(self.project_memory, method_name, None)
        if not callable(method):
            return default
        try:
            value = method()
        except Exception:
            return default
        return value if isinstance(value, dict) else default

    def _read_relationships(self):
        value = self._read_mapping("get_relationships", {"edges": []})
        if isinstance(value, dict):
            value = value.get("edges", [])
        return deepcopy(value) if isinstance(value, list) else []

    @staticmethod
    def _normalize_relative(path):
        return str(path).replace("\\", "/").lstrip("./") if path else ""

    @staticmethod
    def _sorted_mapping(value):
        return {path: value[path] for path in sorted(value)}

    @staticmethod
    def _valid_python_result(result):
        return (
            isinstance(result, dict)
            and isinstance(result.get("symbols"), list)
            and isinstance(result.get("dependencies"), list)
            and isinstance(result.get("definitions"), list)
        )

    def _mark_failed(self, changed_files, error):
        try:
            self.project_memory.set_analysis_state(
                {
                    "status": "failed",
                    "repository_root": str(self.workspace.resolve()),
                    "failed_files": list(changed_files),
                    "error": error,
                }
            )
        except Exception:
            pass
