from agents.base_agent import BaseAgent

from app.core.logger import AppLogger





class ChatAgent(BaseAgent):


    def __init__(
        self,
        llm,
        memory=None,
        conversation=None,
        project_memory=None
    ):


        super().__init__(

            "Chat Agent",

            memory

        )



        self.llm = llm

        self.conversation = conversation

        self.project_memory = project_memory


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

        project_context = ""




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


        if self.project_memory:


            try:


                context = self.project_memory.get_context(
                    message
                )


                if context:


                    project_context = str(
                        context
                    )


            except Exception as error:


                self.logger.error(

                    f"Project memory read error: {error}"

                )



        prompt = f"""
You are AI-Studio Agent.

You are a helpful AI assistant.

Rules:

- Answer in user's language.
- Turkish user -> Turkish.
- English user -> English.
- Be natural and friendly.
- Give useful answers.
- Do not mention internal systems.


Known user information:

{memory_context}



Previous conversation:

{conversation_context}


Project knowledge:

{project_context}


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