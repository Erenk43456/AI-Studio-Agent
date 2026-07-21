from agents.base_agent import BaseAgent
from models.llm import LLM


class ChatAgent(BaseAgent):

    def __init__(self, memory=None):

        super().__init__(
            "Chat Agent",
            memory
        )

        self.llm = LLM()



    def chat(self, message):

        return self.respond(
            message
        )



    def respond(self, message):

        if self.memory:

            self.memory.save(
                "last_message",
                message
            )


        prompt = f"""
Sen Türkçe konuşan profesyonel bir yapay zeka asistanısın.

Kurallar:

- Türkçe cevap ver.
- Yazım hatası yapma.
- Kısa ve doğal cevaplar ver.
- Kullanıcıya yardımcı olmaya çalış.
- Gereksiz uzun açıklamalar yapma.

Kullanıcı:

{message}

Cevap:
"""


        return self.llm.generate(
            prompt
        )