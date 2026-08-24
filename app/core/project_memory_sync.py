from pathlib import Path

from app.core.logger import AppLogger


class ProjectMemorySync:

    def __init__(self, repository_analyzer, project_memory, workspace):
        self.repository_analyzer = repository_analyzer
        self.project_memory = project_memory
        self.workspace = Path(workspace)
        self.logger = AppLogger()

    def sync(self, changed_files):
        if not changed_files:
            return None

        return self._run_full_rescan(
            changed_files,
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
