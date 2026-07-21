from agents.base_agent import BaseAgent
from models.llm import LLM


class ChatAgent(BaseAgent):

    def __init__(self, memory=None):

        super().__init__(
            "Chat Agent",
            memory
        )

        self.llm = LLM()


    def respond(self, message):

        self.memory.save(
            "last_message",
            message
        )

        prompt = f"""
Sen yardımcı bir yapay zeka asistanısın.

Kullanıcı:
{message}

Kısa ve doğal cevap ver.
"""

        return self.llm.generate(prompt)