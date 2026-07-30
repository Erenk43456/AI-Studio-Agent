from agents.base_agent import BaseAgent

from models.llm_provider import LLMProvider
from config.config_manager import ConfigManager

from app.core.logger import AppLogger





class ChatAgent(BaseAgent):


    def __init__(
        self,
        memory=None,
        conversation=None
    ):


        super().__init__(
            "Chat Agent",
            memory
        )


        config = ConfigManager()


        self.llm = LLMProvider(
            config
        )


        self.conversation = conversation


        self.logger = AppLogger()







    def chat(
        self,
        message
    ):


        return self.respond(
            message
        )









    def respond(
        self,
        message
    ):


        self.logger.info(

            f"Chat request: {message}"

        )



        memory_context = ""



        conversation_context = ""





        #
        # Kullanıcı bilgileri
        #

        if self.memory:


            try:


                memories = self.memory.recall()



                important = {}



                for key, value in memories.items():


                    if key not in [

                        "last_task",

                        "last_message"

                    ]:


                        important[key] = value





                if important:


                    memory_context = str(

                        important

                    )



            except Exception as error:


                self.logger.error(

                    f"Memory read error: {error}"

                )








        #
        # Konuşma geçmişi
        #

        if self.conversation:


            try:


                history = self.conversation.get_last(

                    5

                )



                conversation_context = str(

                    history

                )



            except Exception as error:


                self.logger.error(

                    f"Conversation read error: {error}"

                )








        prompt = f"""

You are AI-Studio Agent.

You are a helpful AI assistant.



Rules:

- Answer in user's language.
- Turkish user -> Turkish.
- English user -> English.
- Be natural and friendly.
- Use known information when relevant.
- Do not mention internal systems.
- Do not reveal memory details unless useful.



Known user information:

{memory_context}



Previous conversation:

{conversation_context}



Current user message:

{message}



Assistant response:

"""





        response = self.llm.generate(

            prompt

        )






        if self.memory:


            self.memory.save(

                "last_message",

                message,

                "conversation"

            )





        return response