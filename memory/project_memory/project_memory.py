from datetime import datetime
import hashlib
import json
from pathlib import Path

from app.core.logger import AppLogger
from app.core.storage.json_store import JsonStore


class ProjectMemory:

    def __init__(self, workspace):

        self.workspace = Path(workspace)

        self.memory_path = self.workspace / ".ai_memory"

        self.memory_path.mkdir(parents=True, exist_ok=True)

        self.project_file = self.memory_path / "project.json"

        self.files_file = self.memory_path / "files.json"

        self.architecture_file = self.memory_path / "architecture.json"

        self.symbols_file = self.memory_path / "symbols.json"

        self.dependencies_file = self.memory_path / "dependencies.json"

        self.relationships_file = self.memory_path / "relationships.json"

        self.analysis_state_file = self.memory_path / "analysis_state.json"

        self.project_store = JsonStore(self.project_file)

        self.files_store = JsonStore(self.files_file)

        self.architecture_store = JsonStore(self.architecture_file)

        self.symbols_store = JsonStore(self.symbols_file)

        self.dependencies_store = JsonStore(self.dependencies_file)

        self.relationships_store = JsonStore(self.relationships_file)

        self.analysis_state_store = JsonStore(self.analysis_state_file)

        self.logger = AppLogger()

        self.initialize()

    # =========================================================
    # Initialization
    # =========================================================

    def initialize(self):

        defaults = (
            (
                self.project_store,
                {
                    "name": self.workspace.name,
                    "created": str(datetime.now()),
                    "last_scan": None,
                },
            ),
            (
                self.files_store,
                {},
            ),
            (
                self.architecture_store,
                {},
            ),
            (
                self.symbols_store,
                {},
            ),
            (
                self.dependencies_store,
                {},
            ),
            (
                self.relationships_store,
                {"edges": []},
            ),
            (
                self.analysis_state_store,
                {
                    "schema_version": 2,
                    "status": "uninitialized",
                    "last_full_scan_at": None,
                    "last_incremental_sync_at": None,
                },
            ),
        )

        for store, default in defaults:

            if not store.path.exists():

                store.save(default)

        self.logger.info("Project memory initialized.")

    def has_valid_repository_snapshot(self):
        state = self.get_analysis_state()
        store_generations = state.get("store_generations", {})
        required_stores = {
            "project",
            "files",
            "symbols",
            "dependencies",
            "relationships",
            "architecture",
        }
        return (
            state.get("status") == "ready"
            and bool(state.get("generation_id"))
            and bool(state.get("repository_fingerprint"))
            and state.get("files_indexed") is not None
            and set(store_generations) == required_stores
            and all(
                store_generations[name] == state.get("generation_id")
                for name in required_stores
            )
        )

    # =========================================================
    # JSON compatibility helpers
    # =========================================================

    def save_json(self, path, data):

        path = Path(path)

        store = JsonStore(path)

        store.save(data)

    def load_json(self, path):

        path = Path(path)

        store = JsonStore(path)

        try:

            data = store.load(default={})

        except ValueError as error:

            self.logger.error(f"Project memory JSON error " f"for {path}: {error}")

            return {}

        if not isinstance(data, dict):

            self.logger.warning(f"Project memory data is not " f"a dictionary: {path}")

            return {}

        return data

    # =========================================================
    # Project information
    # =========================================================

    def update_project_info(self, data):

        project = self.project_store.load(default={})

        if not isinstance(project, dict):

            project = {}

        if isinstance(data, dict):

            project.update(data)

        project["last_scan"] = str(datetime.now())

        self.project_store.save(project)

    def sync_repository_analysis(self, analysis):
        """Synchronize a structured repository analysis into memory."""

        analysis = self._coerce_analysis(analysis)

        if not isinstance(analysis, dict):
            self.logger.warning("Repository analysis is not structured data.")
            return False

        generation_id, repository_fingerprint = self._snapshot_identity(analysis)

        overview = analysis.get("overview", {})

        definitions = analysis.get("definitions", {})

        module_roles = analysis.get("module_roles", {})

        if not isinstance(overview, dict):
            return False

        if not isinstance(definitions, dict):
            return False

        if not isinstance(module_roles, dict):
            return False

        project_info = dict(overview)

        project = self.project_store.load(default={})

        if not isinstance(project, dict):
            project = {}

        project.update(
            {
                **project_info,
                "generation_id": generation_id,
                "repository_fingerprint": repository_fingerprint,
                "last_scan": str(datetime.now()),
            }
        )

        if "generated_at" in analysis:
            project["analysis_generated_at"] = analysis["generated_at"]

        indexed_files = analysis.get("files", {})
        if not isinstance(indexed_files, dict):
            indexed_files = {}

        files = {}

        file_paths = set(indexed_files)
        if not file_paths:
            file_paths.update(definitions)
            file_paths.update(module_roles)

        for path in sorted(file_paths):
            info = dict(indexed_files.get(path, {}))
            info["definitions"] = definitions.get(path, info.get("definitions", []))

            if path in module_roles:
                info["role"] = module_roles[path]

            files[str(path).replace("\\", "/")] = info

        try:
            architecture = self.get_architecture()
            architecture["repository_analysis"] = analysis
            architecture["generation_id"] = generation_id

            JsonStore.save_transaction(
                [
                    (
                        self.files_store,
                        files,
                    ),
                    (
                        self.symbols_store,
                        analysis.get(
                            "symbols",
                            {},
                        ),
                    ),
                    (
                        self.dependencies_store,
                        analysis.get(
                            "dependencies",
                            {},
                        ),
                    ),
                    (
                        self.relationships_store,
                        {
                            "edges": analysis.get(
                                "relationships",
                                [],
                            )
                        },
                    ),
                    (
                        self.architecture_store,
                        architecture,
                    ),
                    (
                        self.project_store,
                        project,
                    ),
                ]
            )

            previous_state = self.get_analysis_state()
            sync_mode = analysis.get("sync_mode", "full")

            self.analysis_state_store.save(
                {
                    "schema_version": analysis.get("schema_version", 2),
                    "status": "ready",
                    "generation_id": generation_id,
                    "repository_root": analysis.get("repository_root", ""),
                    "repository_fingerprint": repository_fingerprint,
                    "sync_mode": sync_mode,
                    "last_full_scan_at": (
                        previous_state.get("last_full_scan_at")
                        if sync_mode == "incremental"
                        else analysis.get("generated_at")
                    ),
                    "last_incremental_sync_at": (
                        analysis.get("generated_at")
                        if sync_mode == "incremental"
                        else previous_state.get("last_incremental_sync_at")
                    ),
                    "files_indexed": len(indexed_files),
                    "failed_files": [],
                    "store_generations": {
                        name: generation_id
                        for name in (
                            "project",
                            "files",
                            "symbols",
                            "dependencies",
                            "relationships",
                            "architecture",
                        )
                    },
                }
            )
        except Exception as error:
            self.logger.error(f"Repository memory persistence failed: {error}")
            try:
                self.analysis_state_store.save(
                    {
                        "schema_version": analysis.get("schema_version", 2),
                        "status": "failed",
                        "generation_id": generation_id,
                        "repository_root": analysis.get("repository_root", ""),
                        "repository_fingerprint": repository_fingerprint,
                        "failed_files": [],
                        "error": str(error),
                    }
                )
            except Exception:
                pass
            return False

        self.logger.info("Project memory synchronized from repository analysis.")

        return True

    @staticmethod
    def _snapshot_identity(analysis):
        generation_id = analysis.get("generation_id")
        repository_fingerprint = analysis.get("repository_fingerprint")
        if generation_id and repository_fingerprint:
            return generation_id, repository_fingerprint

        files = analysis.get("files", {})
        if not isinstance(files, dict):
            files = {}
        payload = [
            (path, files[path].get("content_hash", ""))
            for path in sorted(files)
            if isinstance(files[path], dict)
        ]
        repository_fingerprint = (
            "sha256:"
            + hashlib.sha256(
                json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode()
            ).hexdigest()
        )
        generation_id = hashlib.sha256(
            f"repository-analysis-v2:{repository_fingerprint}".encode()
        ).hexdigest()
        return generation_id, repository_fingerprint

    def get_symbols(self):
        return self._load_store(self.symbols_store, {})

    def get_dependencies(self):
        return self._load_store(self.dependencies_store, {})

    def get_relationships(self):
        return self._load_store(
            self.relationships_store,
            {"edges": []},
        )

    def get_analysis_state(self):
        return self._load_store(
            self.analysis_state_store,
            {"status": "uninitialized"},
        )

    def set_analysis_state(self, state):
        current = self.get_analysis_state()
        if isinstance(state, dict):
            current.update(state)
        self.analysis_state_store.save(current)
        return current

    @staticmethod
    def _load_store(store, default):
        try:
            value = store.load(default=default)
        except ValueError:
            return default
        return value if isinstance(value, dict) else default

    @staticmethod
    def _coerce_analysis(analysis):
        if hasattr(analysis, "to_dict"):
            try:
                return analysis.to_dict()
            except Exception:
                return None

        if isinstance(analysis, dict):
            return analysis

        return None

    # =========================================================
    # File memory
    # =========================================================

    def add_file(self, path, info):

        path = str(path).replace("\\", "/")

        files = self.get_all_files()

        files[path] = info

        self.files_store.save(files)

        self.logger.info(f"Project memory updated: {path}")

    def get_file(self, path):

        path = str(path).replace("\\", "/")

        files = self.get_all_files()

        return files.get(path)

    def get_all_files(self):

        try:

            files = self.files_store.load(default={})

        except ValueError as error:

            self.logger.error(f"Failed to load project files: " f"{error}")

            return {}

        if not isinstance(files, dict):

            return {}

        return files

    def remove_file(self, path):

        path = str(path).replace("\\", "/")

        files = self.get_all_files()

        if path not in files:

            return False

        del files[path]

        self.files_store.save(files)

        self.logger.info(f"Project memory removed: {path}")

        return True

    # =========================================================
    # Architecture
    # =========================================================

    def update_architecture(self, name, data):

        architecture = self.get_architecture()

        architecture[name] = data

        self.architecture_store.save(architecture)

    def get_architecture(self):

        try:

            architecture = self.architecture_store.load(default={})

        except ValueError as error:

            self.logger.error(f"Failed to load project architecture: " f"{error}")

            return {}

        if not isinstance(architecture, dict):

            return {}

        return architecture

    # =========================================================
    # Search
    # =========================================================

    def search(self, query):

        if not isinstance(query, str):

            return {}

        query = query.lower().strip()

        if not query:

            return {}

        results = {}

        files = self.get_all_files()

        for path, info in files.items():

            content = self._serialize(info)

            if query in path.lower() or query in content:

                results[path] = info

        return results

    def get_context(self, query, limit=5):

        results = self.search(query)

        context = []

        for path, info in list(results.items())[:limit]:

            context.append(
                {
                    "file": path,
                    "info": info,
                }
            )

        return context

    # =========================================================
    # Utilities
    # =========================================================

    def _serialize(self, value):

        try:

            import json

            return json.dumps(value, ensure_ascii=False, default=str).lower()

        except Exception:

            return str(value).lower()
