from PySide6.QtCore import QThread, Signal



class AIWorker(QThread):

    finished = Signal(str)



    def __init__(
        self,
        planner,
        tool_agent,
        chat_agent,
        conversation,
        message
    ):

        super().__init__()


        self.planner = planner
        self.tool_agent = tool_agent
        self.chat_agent = chat_agent
        self.conversation = conversation
        self.message = message





    def run(self):

        try:

            plan = self.planner.create_plan(
                self.message
            )



            if plan.get("tool") == "chat":


                result = self.chat_agent.chat(
                    self.message
                )



            else:


                result = self.tool_agent.execute(
                    plan
                )



            result = str(result)



        except ConnectionError:


            result = (
                "⚠️ Ollama bağlantısı kurulamadı.\n\n"
                "Lütfen Ollama'nın çalıştığından emin olun."
            )



        except Exception as error:


            print(
                "AI Worker Error:",
                error
            )


            result = (
                "⚠️ Bir hata oluştu:\n"
                f"{error}"
            )




        try:

            self.conversation.add(
                self.message,
                result
            )


        except Exception as error:


            print(
                "Conversation save error:",
                error
            )




        self.finished.emit(
            result
        )