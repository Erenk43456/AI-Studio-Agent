import logging
from pathlib import Path



class AppLogger:


    def __init__(self):

        log_dir = Path("logs")

        log_dir.mkdir(
            exist_ok=True
        )


        self.file = log_dir / "app.log"



        logging.basicConfig(

            level=logging.INFO,

            format=(
                "%(asctime)s | "
                "%(levelname)s | "
                "%(name)s | "
                "%(message)s"
            ),

            handlers=[

                logging.FileHandler(
                    self.file,
                    encoding="utf-8"
                ),

                logging.StreamHandler()

            ]

        )



        self.logger = logging.getLogger(
            "AI-Studio-Agent"
        )





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