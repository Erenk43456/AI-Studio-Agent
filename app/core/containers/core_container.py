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
        # WORKSPACE
        #

        sandbox_path = (
            Path.home()
            /
            "Desktop"
            /
            "AI-Studio-Workspace"
        )


        self.workspace = WorkspaceManager(
            sandbox_path
        )


        self.workspace_path = (
            self.workspace.create_workspace()
        )