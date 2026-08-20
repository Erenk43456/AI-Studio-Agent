from app.core.logger import AppLogger


class ProjectMemorySync:

    def __init__(
        self,
        repository_analyzer,
        project_memory,
        workspace
    ):
        self.repository_analyzer = (
            repository_analyzer
        )

        self.project_memory = (
            project_memory
        )

        self.workspace = workspace

        self.logger = AppLogger()

    def sync(
        self,
        changed_files
    ):
        if not changed_files:
            return None

        try:
            result = self.repository_analyzer.analyze(
                self.workspace
            )

            if result is None:
                return None

            if not self.project_memory.sync_repository_analysis(
                result
            ):
                return None

            return result

        except Exception as error:
            self.logger.error(
                f"Project memory sync failed: {error}"
            )

            return None