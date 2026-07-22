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
        # Greetings
        #

        greetings = [
            "merhaba",
            "selam",
            "hey",
            "hi",
            "hello",
            "nasılsın",
            "teşekkür",
            "sağol"
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
        # Direct math expression
        #

        expression = re.search(
            r"(\d+)\s*([\+\-\*/])\s*(\d+)",
            task
        )


        if expression:

            a = int(
                expression.group(1)
            )

            operator = expression.group(2)

            b = int(
                expression.group(3)
            )


            operations = {

                "+": "add",
                "-": "subtract",
                "*": "multiply",
                "/": "divide"

            }


            return {

                "tool": "calculator",

                "operation": operations[operator],

                "numbers": [
                    a,
                    b
                ]

            }




        #
        # Turkish math commands
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
            "kat",

            "böl",
            "bol"

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



            elif (
                "çarp" in task
                or "carp" in task
                or "kat" in task
            ):

                operation = "multiply"



            elif (
                "böl" in task
                or "bol" in task
            ):

                operation = "divide"



            return {

                "tool": "calculator",

                "operation": operation,

                "numbers": [

                    int(numbers[0]),
                    int(numbers[1])

                ]

            }




        #
        # Memory
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
        ):

            return {

                "tool": "memory_get",

                "key": "favori_oyun"

            }




        #
        # Save name
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
You are an AI agent planner.

Return JSON only.

Available tools:

calculator:
Math operations.

memory_save:
Save information.

memory_get:
Retrieve information.

file:
File operations.

chat:
Normal conversation.


Rules:

- Return only JSON.
- No explanations.
- Use chat for normal conversation.


User:

{task}
"""



        try:

            response = self.llm.generate(
                prompt
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
                "Planner error:",
                error
            )


            return {

                "tool": "chat",

                "message": task

            }