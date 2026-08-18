from datetime import datetime
from pathlib import Path

from app.core.logger import AppLogger
from app.core.storage.json_store import JsonStore


class ProjectMemory:

    def __init__(
        self,
        workspace
    ):

        self.workspace = Path(
            workspace
        )

        self.memory_path = (
            self.workspace
            / ".ai_memory"
        )

        self.memory_path.mkdir(
            parents=True,
            exist_ok=True
        )

        self.project_file = (
            self.memory_path
            / "project.json"
        )

        self.files_file = (
            self.memory_path
            / "files.json"
        )

        self.architecture_file = (
            self.memory_path
            / "architecture.json"
        )

        self.project_store = JsonStore(
            self.project_file
        )

        self.files_store = JsonStore(
            self.files_file
        )

        self.architecture_store = JsonStore(
            self.architecture_file
        )

        self.logger = AppLogger()

        self.initialize()

    # =========================================================
    # Initialization
    # =========================================================

    def initialize(
        self
    ):

        defaults = (
            (
                self.project_store,
                {
                    "name": self.workspace.name,
                    "created": str(
                        datetime.now()
                    ),
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
        )

        for store, default in defaults:

            if not store.path.exists():

                store.save(
                    default
                )

        self.logger.info(
            "Project memory initialized."
        )

    # =========================================================
    # JSON compatibility helpers
    # =========================================================

    def save_json(
        self,
        path,
        data
    ):

        path = Path(
            path
        )

        store = JsonStore(
            path
        )

        store.save(
            data
        )

    def load_json(
        self,
        path
    ):

        path = Path(
            path
        )

        store = JsonStore(
            path
        )

        try:

            data = store.load(
                default={}
            )

        except ValueError as error:

            self.logger.error(
                f"Project memory JSON error "
                f"for {path}: {error}"
            )

            return {}

        if not isinstance(
            data,
            dict
        ):

            self.logger.warning(
                f"Project memory data is not "
                f"a dictionary: {path}"
            )

            return {}

        return data

    # =========================================================
    # Project information
    # =========================================================

    def update_project_info(
        self,
        data
    ):

        project = self.project_store.load(
            default={}
        )

        if not isinstance(
            project,
            dict
        ):

            project = {}

        if isinstance(
            data,
            dict
        ):

            project.update(
                data
            )

        project["last_scan"] = str(
            datetime.now()
        )

        self.project_store.save(
            project
        )

    # =========================================================
    # File memory
    # =========================================================

    def add_file(
        self,
        path,
        info
    ):

        path = str(
            path
        ).replace(
            "\\",
            "/"
        )

        files = self.get_all_files()

        files[path] = info

        self.files_store.save(
            files
        )

        self.logger.info(
            f"Project memory updated: {path}"
        )

    def get_file(
        self,
        path
    ):

        path = str(
            path
        ).replace(
            "\\",
            "/"
        )

        files = self.get_all_files()

        return files.get(
            path
        )

    def get_all_files(
        self
    ):

        try:

            files = self.files_store.load(
                default={}
            )

        except ValueError as error:

            self.logger.error(
                f"Failed to load project files: "
                f"{error}"
            )

            return {}

        if not isinstance(
            files,
            dict
        ):

            return {}

        return files

    def remove_file(
        self,
        path
    ):

        path = str(
            path
        ).replace(
            "\\",
            "/"
        )

        files = self.get_all_files()

        if path not in files:

            return False

        del files[path]

        self.files_store.save(
            files
        )

        self.logger.info(
            f"Project memory removed: {path}"
        )

        return True

    # =========================================================
    # Architecture
    # =========================================================

    def update_architecture(
        self,
        name,
        data
    ):

        architecture = self.get_architecture()

        architecture[name] = data

        self.architecture_store.save(
            architecture
        )

    def get_architecture(
        self
    ):

        try:

            architecture = (
                self.architecture_store.load(
                    default={}
                )
            )

        except ValueError as error:

            self.logger.error(
                f"Failed to load project architecture: "
                f"{error}"
            )

            return {}

        if not isinstance(
            architecture,
            dict
        ):

            return {}

        return architecture

    # =========================================================
    # Search
    # =========================================================

    def search(
        self,
        query
    ):

        if not isinstance(
            query,
            str
        ):

            return {}

        query = query.lower().strip()

        if not query:

            return {}

        results = {}

        files = self.get_all_files()

        for path, info in files.items():

            content = self._serialize(
                info
            )

            if (
                query in path.lower()
                or query in content
            ):

                results[path] = info

        return results

    def get_context(
        self,
        query,
        limit=5
    ):

        results = self.search(
            query
        )

        context = []

        for path, info in list(
            results.items()
        )[:limit]:

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

    def _serialize(
        self,
        value
    ):

        try:

            import json

            return json.dumps(
                value,
                ensure_ascii=False,
                default=str
            ).lower()

        except Exception:

            return str(
                value
            ).lower()