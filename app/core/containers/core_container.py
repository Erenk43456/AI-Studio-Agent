from pathlib import Path

from config.config_manager import ConfigManager
from app.core.workspace.workspace_manager import WorkspaceManager


class CoreContainer:

    def __init__(self):

        #
        # CONFIG
        #

        self.config = ConfigManager()


        #
        # PROJECT SOURCE
        #

        project_root = (
            Path(__file__)
            .resolve()
            .parents[3]
        )


        #
        # WORKSPACE
        #

        self.workspace = WorkspaceManager(
            project_root
        )


        self.workspace_path = (
            self.workspace.create_workspace()
        )