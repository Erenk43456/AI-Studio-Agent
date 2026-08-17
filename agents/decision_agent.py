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
        # Calculator / Tool Requests
        #
        # Tools are not top-level systems.
        # Calculator and other tools are handled
        # through the Development system.
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
                "system": "development",
                "reason": (
                    "Calculation request should be handled "
                    "by the development tool layer."
                )
            }

        #
        # Development
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
            "architecture",
            "dosya",
            "file",
            "oku",
            "okuma",
            "yaz",
            "yazma",
            "sil",
            "oluştur",
            "olustur"
        ]

        if any(
            re.search(
                rf"\b{re.escape(word)}\b",
                request_lower
            )
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
- Dosya oluşturma
- Dosya okuma
- Dosya yazma
- Dosya değiştirme
- Dosya işlemleri
- Hesaplama
- Tool kullanımı
- Bug düzeltme
- Refactor
- Yeni özellik geliştirme

Kurallar:

Yazılım, proje, repository, kod veya dosya ile
ilgili tüm isteklerde:

development seç.

Dosya oluşturma, okuma, yazma veya değiştirme
isteklerinde:

development seç.

Hesaplama veya calculator kullanımı gerektiren
isteklerde:

development seç.

Bir tool kullanılması gerekiyorsa:

tool'u SYSTEM olarak seçme.

Tool seçimini planning/execution katmanına bırak.

Kullanıcı bilgisi veya hatırlama isteklerinde:

memory seç.

Sadece normal konuşmalarda:

chat seç.

Geçerli SYSTEM değerleri yalnızca şunlardır:

memory
chat
development

Başka hiçbir SYSTEM değeri üretme.

Sadece JSON döndür.

Format:

{{
    "system": "chat",
    "reason": "neden bu sistem seçildi"
}}

Kullanıcı:

{request}
"""

        try:

            response = self.llm.generate(
                prompt,
                temperature=0.1
            )

            #
            # Direct dictionary response
            #

            if isinstance(
                response,
                dict
            ):

                decision = response

            else:

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

                if not match:

                    raise ValueError(
                        "Decision model did not return valid JSON."
                    )

                decision = json.loads(
                    match.group()
                )

            #
            # Decision Validation
            #

            allowed_systems = {
                "chat",
                "memory",
                "development"
            }

            system = decision.get(
                "system"
            )

            if system not in allowed_systems:

                self.logger.warning(
                    "Invalid system returned by "
                    f"DecisionAgent: {system}"
                )

                return {
                    "system": "development",
                    "reason": (
                        "Invalid system returned by "
                        "decision model."
                    )
                }

            return decision

        except Exception as error:

            self.logger.error(
                f"Decision error: {error}"
            )

            return {
                "system": "chat",
                "reason": "fallback"
            }