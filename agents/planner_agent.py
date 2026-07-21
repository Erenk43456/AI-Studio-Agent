from agents.base_agent import BaseAgent
from models.llm import LLM
import json
import re


class PlannerAgent(BaseAgent):

    def __init__(self):
        super().__init__("Planner Agent")
        self.llm = LLM()


    def create_plan(self, task):

        task = task.lower()

        self.memory.save("last_task", task)


        prompt = f"""
Sen bir AI agent planlayıcısısın.

Sadece JSON döndür.

Kullanılabilir araçlar:

memory_save:
Kullanıcı yeni bir bilgi veriyorsa kullan.

Bilginin anahtarını kısa ve Türkçe seç.

Örnekler:

Kullanıcı:
benim arabam renault clio

JSON:
{{
"tool":"memory_save",
"key":"araba",
"value":"renault clio"
}}


Kullanıcı:
kedimin adı pamuk

JSON:
{{
"tool":"memory_save",
"key":"kedi_adi",
"value":"pamuk"
}}


Kullanıcı:
sevdiğim renk kırmızı

JSON:
{{
"tool":"memory_save",
"key":"favori_renk",
"value":"kırmızı"
}}


memory_get:
Kullanıcı daha önce söylediği bir bilgiyi soruyorsa kullan.

Örnek:

Kullanıcı:
arabam ne

JSON:
{{
"tool":"memory_get",
"key":"araba"
}}


Kullanıcı:
kedimin adı ne

JSON:
{{
"tool":"memory_get",
"key":"kedi_adi"
}}


Kurallar:
- Sadece JSON yaz.
- Açıklama yazma.
- memory_save kullanırken key ve value zorunludur.


Kullanıcı:
{task}
"""


        response = self.llm.generate(prompt)


        print("\nLLM cevabı:")
        print(response)


        response = response.replace("```json", "")
        response = response.replace("```", "")


        try:

            plan = json.loads(response)


            if plan.get("tool") == "memory_save":

                if "value" not in plan:
                    plan["value"] = task


                if "key" not in plan:
                    plan["key"] = "bilgi"


            return plan


        except:

            return {
                "tool": None
            }