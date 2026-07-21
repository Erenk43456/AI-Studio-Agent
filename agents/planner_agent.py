from agents.base_agent import BaseAgent
from models.llm import LLM

import json
import re



class PlannerAgent(BaseAgent):

    def __init__(
        self,
        memory=None
    ):

        super().__init__(
            "Planner Agent",
            memory
        )

        self.llm = LLM()



    def clean_json(
        self,
        text
    ):

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




    def create_plan(
        self,
        task
    ):

        task = task.lower().strip()



        # =========================
        # Kesin hafıza sorguları
        # =========================


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
            or "en sevdiğim oyun ne" in task
        ):

            return {

                "tool": "memory_get",

                "key": "favori_oyun"

            }




        # =========================
        # Kesin hafıza kayıtları
        # =========================


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





        if task.startswith(
            "favori oyunum "
        ):

            return {

                "tool": "memory_save",

                "key": "favori_oyun",

                "value": task.replace(
                    "favori oyunum",
                    ""
                ).strip()

            }




        # =========================
        # Genel görevler için memory
        # =========================


        if self.memory:

            self.memory.save(
                "last_task",
                task
            )




        prompt = f"""
Sen bir AI agent planlayıcısısın.

Sadece JSON döndür.

Kullanılabilir araçlar:


calculator:

Matematik işlemleri için kullan.

Örnek:

Kullanıcı:
20 ile 30'u topla

Cevap:

{{
"tool":"calculator",
"operation":"add",
"numbers":[20,30]
}}



memory_save:

Yeni bilgi kaydetmek için kullan.

Format:

{{
"tool":"memory_save",
"key":"kisa_turkce_isim",
"value":"bilgi"
}}



memory_get:

Daha önce kaydedilmiş bilgi istenirse kullan.

Format:

{{
"tool":"memory_get",
"key":"bilgi_adi"
}}



file:

Dosya işlemleri için kullan.



chat:

Normal sohbet için kullan.


Kurallar:

- Sadece JSON yaz.
- Açıklama yazma.
- JSON dışında hiçbir şey yazma.


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

            print(
                response
            )



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