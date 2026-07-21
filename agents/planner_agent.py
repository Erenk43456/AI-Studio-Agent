from agents.base_agent import BaseAgent
from models.llm import LLM

import json
import re


class PlannerAgent(BaseAgent):

    def __init__(self, memory=None):
        super().__init__("Planner Agent")

        self.llm = LLM()
        self.memory = memory


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

        return text


    def create_plan(self, task):

        task = task.lower().strip()


        if self.memory:
            self.memory.save(
                "last_task",
                task
            )


        prompt = f"""
Sen bir AI agent planlayıcısısın.

Sadece JSON döndür.

Araçlar:

memory_save:
Kullanıcı yeni bilgi verirse.

Format:
{{
"tool":"memory_save",
"key":"bilgi_adi",
"value":"bilgi"
}}


memory_get:
Kullanıcı eski bilgi sorarsa.

Format:
{{
"tool":"memory_get",
"key":"bilgi_adi"
}}


calculator:
Matematik işlemlerinde kullan.


file:
Dosya işlemlerinde kullan.


Kurallar:
- Sadece JSON döndür.
- Açıklama yazma.


Kullanıcı:
{task}
"""


        try:

            response = self.llm.generate(prompt)


            print("\nLLM cevabı:")
            print(response)


            response = self.clean_json(response)


            plan = json.loads(response)


            if "tool" not in plan:
                plan["tool"] = None


            return plan


        except json.JSONDecodeError:

            return {
                "tool": None
            }


        except Exception as error:

            print(
                "Planner hatası:",
                error
            )

            return {
                "tool": None
            }