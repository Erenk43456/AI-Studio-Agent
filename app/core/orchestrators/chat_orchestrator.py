from app.core.logger import AppLogger



class ChatOrchestrator:


    def __init__(
        self,
        container
    ):


        self.container = container


        self.chat_agent = (
            container.chat_agent
        )


        self.logger = AppLogger()



    def run(
        self,
        message,
        decision=None,
        conversation=None,
        execution=None
    ):


        self.logger.info(
            f"Chat request: {message}"
        )



        if conversation is not None:

            self.chat_agent.conversation = (
                conversation
            )



        return self.chat_agent.chat(

            message

        )