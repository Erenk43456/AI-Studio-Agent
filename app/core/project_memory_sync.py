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

        plan = {
            "action": "analyze",
            "path": str(self.workspace),
            "changed_files": changed_files,
        }

        try:
            result = self.repository_analyzer.execute(
                plan
            )

            if result is None:
                return None

            self.project_memory.update_architecture(
                "repository_analysis",
                result
            )

            return result

        except Exception as error:
            self.logger.error(
                f"Project memory sync failed: {error}"
            )

            return None