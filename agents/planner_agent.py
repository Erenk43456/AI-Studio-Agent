from agents.base_agent import BaseAgent
from models.llm import LLM

import json
import re


class PlannerAgent(BaseAgent):

    def __init__(self, memory=None):

        super().__init__(
            "Planner Agent",
            memory
        )

        self.llm = LLM()


    def clean_json(self, text):

        text = text.strip()

        text = text.replace(
            "```json",
            ""
        )

        text = text.replace(
            "```",
            ""
        )

        match = re.search(
            r"\{.*\}",
            text,
            re.DOTALL
        )

        if match:
            return match.group()

        return "{}"



    def create_plan(self, task):

        task = task.lower().strip()


        #
        # Normal sohbet
        #

        greetings = [
            "merhaba",
            "selam",
            "selaam",
            "hey",
            "hi",
            "hello"
        ]


        if task in greetings:

            return {
                "tool": "chat",
                "message": task
            }



        #
        # Hafıza sorguları
        #

        if (
            "adım ne" in task
            or "ismim ne" in task
            or "ben kimim" in task
        ):

            return {
                "tool": "memory_get",
                "key": "isim"
            }



        if (
            "favori oyunum ne" in task
            or "favori oyunum nedir" in task
        ):

            return {
                "tool": "memory_get",
                "key": "favori_oyun"
            }



        #
        # İsim kaydetme
        #

        if task.startswith(
            "benim adım "
        ):

            return {

                "tool": "memory_save",

                "key": "isim",

                "value": task.replace(
                    "benim adım",
                    ""
                ).strip()

            }



        self.memory.save(
            "last_task",
            task
        )



        prompt = f"""
Sen bir AI agent planlayıcısısın.

Sadece JSON döndür.

Araçlar:

calculator:
Matematik işlemleri için.

Format:

{{
"tool":"calculator",
"operation":"add",
"numbers":[20,30]
}}



memory_save:
Yeni bilgi kaydetmek için.

Format:

{{
"tool":"memory_save",
"key":"isim",
"value":"eren"
}}



memory_get:
Kayıtlı bilgi almak için.

Format:

{{
"tool":"memory_get",
"key":"isim"
}}



file:
Dosya işlemleri için.



chat:
Normal konuşmalar için.

Format:

{{
"tool":"chat",
"message":"cevap"
}}



Kurallar:

- Sadece JSON döndür.
- Açıklama yazma.
- Selamlaşmaları memory olarak kaydetme.
- Bilgi kaydetme isteği yoksa memory kullanma.


Kullanıcı:

{task}
"""



        try:

            response = self.llm.generate(
                prompt
            )


            print(
                "\nLLM cevabı:"
            )

            print(response)



            response = self.clean_json(
                response
            )


            plan = json.loads(
                response
            )


            if "tool" not in plan:

                plan["tool"] = "chat"



            return plan



        except Exception as error:

            print(
                "Planner hatası:",
                error
            )


            return {
                "tool": "chat",
                "message": task
            }