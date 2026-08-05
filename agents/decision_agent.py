import json
import re

from agents.base_agent import BaseAgent
from app.core.logger import AppLogger



class DecisionAgent(BaseAgent):


    def __init__(
        self,
        llm,
        memory,
        registry
    ):

        super().__init__(
            "Decision Agent"
        )


        self.llm = llm

        self.memory = memory

        self.registry = registry

        self.logger = AppLogger()





    def process(
        self,
        request
    ):


        self.logger.info(
            f"Decision request: {request}"
        )


        request_lower = request.lower()






        #
        # Memory
        #

        if any(
            word in request_lower
            for word in [
                "ismim ne",
                "ben kimim",
                "adım ne"
            ]
        ):


            return {

                "system": "memory",

                "action": "get"

            }






        if "benim adım" in request_lower:


            return {

                "system": "memory",

                "action": "save"

            }









        #
        # Calculator
        #

        calculation_words = [

            "topla",
            "çıkar",
            "cikar",
            "çarp",
            "carp",
            "böl",
            "bol"

        ]


        if (
            any(
                word in request_lower
                for word in calculation_words
            )
            or
            re.search(
                r"\d+\s*[\+\-\*\/]\s*\d+",
                request_lower
            )
        ):


            return {

                "system": "tool",

                "tool": "calculator"

            }









        #
        # Code
        #

        code_keywords = [

            "kod",
            "code",
            ".py",
            "bug",
            "hata",
            "düzelt",
            "duzelt",
            "refactor",
            "implement",
            "oluştur",
            "olustur",
            "geliştir",
            "gelistir",
            "repository",
            "repo",
            "mimari",
            "architecture"

        ]


        if any(

            word in request_lower

            for word in code_keywords

        ):


            return {

                "system": "development"

            }









        #
        # LLM Decision
        #

        prompt = f"""

Sen AI-Studio Master Decision Agent'sın.

Görevin kullanıcı isteğini analiz etmek ve
hangi SYSTEM'in çalışacağını seçmektir.

Mevcut sistemler:

memory:
- Kullanıcı bilgisi kaydetme
- Kullanıcı bilgisi getirme
- Hafıza işlemleri


chat:
- Genel sohbet
- Soru cevap
- Açıklama
- Normal konuşmalar


development:
- Yazılım geliştirme
- Kod yazma
- Kod analizi
- Repository inceleme
- Dosya yapısı analizi
- Bug düzeltme
- Refactor
- Yeni özellik geliştirme


tool:
- Hesaplama
- Basit araç kullanımı
- Özel yardımcı işlemler


Kurallar:

Yazılım, proje, repository veya kod ile ilgili tüm isteklerde:
development seç.

Sadece normal konuşmalarda:
chat seç.

Kullanıcı bilgisi veya hatırlama isteklerinde:
memory seç.

Hesaplama veya basit araç kullanımında:
tool seç.


Sadece JSON döndür.

Format:

{{
    "system":"chat",
    "reason":"neden bu sistem seçildi"
}}


Kullanıcı:

{request}

"""



        try:


            response = self.llm.generate(

                prompt,

                temperature=0.1

            )



            if isinstance(
                response,
                dict
            ):

                return response





            response = response.strip()



            #
            # Markdown temizleme
            #

            response = re.sub(

                r"```json|```",

                "",

                response

            ).strip()






            #
            # JSON bloğu yakalama
            #

            match = re.search(

                r"\{.*\}",

                response,

                re.DOTALL

            )


            if match:


                response = match.group()





            return json.loads(
                response
            )






        except Exception as e:


            self.logger.error(

                f"Decision error: {e}"

            )



            return {

                "system":"chat",

                "reason":"fallback"

            }