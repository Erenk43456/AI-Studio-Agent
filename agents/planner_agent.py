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
        # Normal conversation / greetings
        #

        greetings = [
            "merhaba",
            "selam",
            "selaam",
            "hey",
            "hi",
            "hello",
            "nasılsın",
            "sen nasılsın",
            "iyi misin",
            "iyiyim",
            "teşekkür",
            "tesekkur",
            "sağol",
            "sağ ol"
        ]



        if any(
            word in task
            for word in greetings
        ):

            return {
                "tool": "chat",
                "message": task
            }





        #
        # Math detection
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
        # Memory queries
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
        # Name storage
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
        # Save last task
        #

        self.memory.save(
            "last_task",
            task
        )





        prompt = f"""
You are an AI agent planner.

Return JSON only.

Available tools:

calculator:
Used for mathematical operations.

Example:

{{
"tool":"calculator",
"operation":"add",
"numbers":[20,30]
}}


memory_save:
Used to store new information.


memory_get:
Used to retrieve stored information.


file:
Used for file operations.


chat:
Used for normal conversations.


Rules:

- Return JSON only.
- Do not write explanations.
- Use chat for normal conversations.
- Do not use memory unless the user wants to save or retrieve information.
- Always select the most appropriate tool.


User request:

{task}
"""



        try:

            response = self.llm.generate(
                prompt
            )



            print(
                "\nLLM response:"
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
                "Planner error:",
                error
            )



            return {
                "tool": "chat",
                "message": task
            }