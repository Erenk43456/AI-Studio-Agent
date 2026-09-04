import logging
from pathlib import Path



class AppLogger:


    def __init__(self):

        log_dir = Path("logs")

        log_dir.mkdir(
            exist_ok=True
        )

        self.file = log_dir / "app.log"

        self.logger = logging.getLogger(
            "AI-Studio-Agent"
        )

        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            formatter = logging.Formatter(
                "%(asctime)s | "
                "%(levelname)s | "
                "%(name)s | "
                "%(message)s"
            )

            file_handler = logging.FileHandler(
                self.file,
                encoding="utf-8"
            )

            stream_handler = logging.StreamHandler()

            file_handler.setFormatter(formatter)
            stream_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)
            self.logger.addHandler(stream_handler)

            self.logger.propagate = False



    def info(
        self,
        message
    ):

        self.logger.info(
            message
        )



    def error(
        self,
        message
    ):

        self.logger.error(
            message
        )



    def warning(
        self,
        message
    ):

        self.logger.warning(
            message
        )