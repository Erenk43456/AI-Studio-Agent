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


        if self.isRunning():


            self.quit()

            self.wait()