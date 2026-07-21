from PySide6.QtCore import QThread, Signal


class AIWorker(QThread):

    finished = Signal(str)

    def __init__(
        self,
        planner,
        tool_agent,
        chat_agent,
        message
    ):
        super().__init__()

        self.planner = planner
        self.tool_agent = tool_agent
        self.chat_agent = chat_agent
        self.message = message


    def run(self):

        plan = self.planner.create_plan(
            self.message
        )


        if plan["tool"] == "chat":

            result = self.chat_agent.chat(
                self.message
            )

        else:

            result = self.tool_agent.execute(
                plan
            )


        self.finished.emit(
            str(result)
        )