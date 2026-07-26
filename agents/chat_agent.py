from agents.base_agent import BaseAgent

from models.llm_provider import LLMProvider
from config.config_manager import ConfigManager



class ChatAgent(BaseAgent):


    def __init__(
        self,
        memory=None
    ):


        super().__init__(
            "Chat Agent",
            memory
        )


        config = ConfigManager()


        self.llm = LLMProvider(
            config
        )




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


        if self.memory:


            self.memory.save(
                "last_message",
                message
            )



        prompt = f"""
You are a professional AI assistant.

Rules:

- Respond naturally based on the user's language.
- If the user speaks Turkish, answer in Turkish.
- If the user speaks English, answer in English.
- Provide clear and helpful answers.
- Avoid unnecessary explanations.
- Maintain a friendly and professional tone.

User:

{message}

Response:
"""



        return self.llm.generate(
            prompt
        )