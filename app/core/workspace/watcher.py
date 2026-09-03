from pathlib import Path
import time
from threading import Thread

from app.core.logger import AppLogger


SKIP_DIRS = {
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "data",
    ".ai_memory",
    "logs",
    "build",
    "dist",
}



class WorkspaceWatcher:


    def __init__(
        self,
        workspace,
        callback
    ):

        self.workspace = Path(workspace)

        self.callback = callback

        self.running = False

        self.files = {}

        self.logger = AppLogger()



    def scan(self):

        current = {}


        for file in self.workspace.rglob("*"):

            if not file.is_file():
                continue

            if any(
                part in SKIP_DIRS
                for part in file.parts
            ):
                continue


            try:

                current[str(file)] = (
                    file.stat().st_mtime
                )


            except OSError as error:

                self.logger.error(
                    f"File scan error {file}: {error}"
                )


        return current





    def start(self):

        self.files = self.scan()

        self.running = True


        thread = Thread(
            target=self.loop,
            daemon=True
        )


        thread.start()


        self.logger.info(
            "Workspace watcher started."
        )






    def stop(self):

        self.running = False


        self.logger.info(
            "Workspace watcher stopped."
        )







    def detect_changes(
        self,
        current
    ):


        changed_files = []


        #
        # New or modified files
        #

        for file, modified_time in current.items():


            old_time = self.files.get(
                file
            )


            if old_time != modified_time:

                changed_files.append(
                    file
                )



        #
        # Deleted files
        #

        for file in self.files:


            if file not in current:

                changed_files.append(
                    file
                )


        return changed_files







    def loop(self):


        while self.running:


            try:

                time.sleep(10)


                current = self.scan()


                changed_files = self.detect_changes(
                    current
                )



                if changed_files:


                    self.logger.info(
                        f"Workspace changes detected: {changed_files}"
                    )


                    self.callback(
                        changed_files
                    )



                    self.files = current



            except Exception as error:


                self.logger.error(
                    f"Workspace watcher error: {error}"
                )