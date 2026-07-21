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
        # Selamlaşma
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
                "message": "Merhaba! Nasıl yardımcı olabilirim?"
            }




        #
        # Matematik algılama
        #

        numbers = re.findall(
            r"\d+",
            task
        )


        math_words = [
            "topla",
            "ekle",
            "arttır",
            "artir",
            "çıkar",
            "cikar",
            "eksi",
            "çarp",
            "carp",
            "kat"
        ]


        if (
            len(numbers) >= 2
            and any(
                word in task
                for word in math_words
            )
        ):

            operation = "add"


            if (
                "çıkar" in task
                or "cikar" in task
                or "eksi" in task
            ):
                operation = "subtract"


            if (
                "çarp" in task
                or "carp" in task
                or "kat" in task
            ):
                operation = "multiply"



            return {
                "tool": "calculator",
                "operation": operation,
                "numbers": [
                    int(numbers[0]),
                    int(numbers[1])
                ]
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




        #
        # Son görev kaydı
        #

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


memory_get:
Kayıtlı bilgi almak için.


file:
Dosya işlemleri için.


chat:
Normal konuşmalar için.


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