import shutil
from pathlib import Path

from app.core.logger import AppLogger



class WorkspaceManager:


    def __init__(
        self,
        source_path
    ):

        self.logger = AppLogger()

        self.source_path = Path(
            source_path
        )


        self.desktop = Path.home() / "Desktop"


        self.workspace_root = (
            self.desktop /
            "AI-Studio-Workspace"
        )





    def create_workspace(self):


        try:


            # Workspace zaten varsa dokunma
            if self.workspace_root.exists():

                self.logger.info(

                    f"Existing workspace found: {self.workspace_root}"

                )


                return str(
                    self.workspace_root
                )





            # İlk defa oluştur

            shutil.copytree(

                self.source_path,

                self.workspace_root,

                ignore=shutil.ignore_patterns(

                    ".git",

                    "__pycache__",

                    ".venv",

                    "venv"

                )

            )



            self.logger.info(

                f"Workspace created: {self.workspace_root}"

            )


            return str(
                self.workspace_root
            )




        except Exception as error:


            self.logger.error(

                f"Workspace creation error: {error}"

            )


            return None





    def reset_workspace(self):

        """
        Workspace'i ana klasörden tekrar oluşturur.
        Manuel sıfırlama için kullanılır.
        """

        try:

            if self.workspace_root.exists():

                shutil.rmtree(
                    self.workspace_root
                )


            return self.create_workspace()


        except Exception as error:


            self.logger.error(

                f"Workspace reset error: {error}"

            )


            return None





    def get_workspace(self):


        if self.workspace_root.exists():

            return str(
                self.workspace_root
            )


        return None