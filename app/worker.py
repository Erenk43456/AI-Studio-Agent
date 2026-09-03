import threading

from PySide6.QtCore import QThread, Signal


class AIWorker(QThread):


    finished = Signal(str)



    def __init__(
        self,
        orchestrator,
        conversation,
        message
    ):

        super().__init__()


        self.orchestrator = orchestrator

        self.conversation = conversation

        self.message = message

        self.cancel_event = threading.Event()

        container = getattr(
            orchestrator,
            "container",
            None
        )

        if container is not None:

            models = getattr(
                container,
                "models",
                None
            )

            if models is not None:

                models.set_cancel_event(
                    self.cancel_event
                )


    def run(self):

        try:


            result = self.orchestrator.run(

                self.message,

                self.conversation

            )


            self.finished.emit(

                str(result)

            )



        except Exception as error:


            self.finished.emit(

                f"AI Error: {error}"

            )







    def stop(self):

        self.cancel_event.set()