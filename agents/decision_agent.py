import json
import re

from agents.base_agent import BaseAgent
from agents.contract_agent import ContractAgent
from agents.contracts.decision import DecisionContract
from app.core.logger import AppLogger


class DecisionAgent(BaseAgent):

    def __init__(
        self,
        llm,
        memory,
        registry,
        contract_agent=None,
    ):

        super().__init__(
            "Decision Agent"
        )

        self.llm = llm
        self.memory = memory
        self.registry = registry
        self.contract_agent = contract_agent or ContractAgent()
        self.logger = AppLogger()

    def process(
        self,
        request
    ) -> DecisionContract:

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

            return self.contract_agent.to_decision_contract({
                "system": "memory",
                "action": "get"
            })

        if "benim adım" in request_lower:

            return self.contract_agent.to_decision_contract({
                "system": "memory",
                "action": "save"
            })


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

            return self.contract_agent.to_decision_contract({
                "system": "development",
                "reason": (
                    "Calculation request should be handled "
                    "by the development tool layer."
                )
            })

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
        ]

        if any(
            re.search(
                rf"\b{re.escape(word)}\b",
                request_lower
            )
            for word in code_keywords
        ):
            #
            # Explicit code-changing requests have priority
            # over generic analysis/improvement wording.
            #

            code_action_keywords = [
                "düzelt",
                "duzelt",
                "fix",
                "değiştir",
                "degistir",
                "yaz",
                "oluştur",
                "olustur",
                "ekle",
                "sil",
                "implement",
                "uygula",
            ]

            improve_keywords = [
                "iyileştir",
                "iyilestir",
                "improve",
                "optimize",
                "geliştir",
                "gelistir",
                "refactor",
            ]

            analyze_keywords = [
                "analiz",
                "incele",
                "inceleme",
                "değerlendir",
                "degerlendir",
                "kontrol et",
                "gözden geçir",
                "gozden gecir",
                "tespit et",
            ]

            if any(
                word in request_lower
                for word in code_action_keywords
            ):
                action = "code"

            elif any(
                word in request_lower
                for word in improve_keywords
            ):
                action = "improve"

            elif any(
                word in request_lower
                for word in analyze_keywords
            ):
                action = "analyze"

            else:
                action = "code"

            return self.contract_agent.to_decision_contract({
                "system": "development",
                "action": action,
            })


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

            if isinstance(decision, dict):
                system = decision.get("system")
            else:
                system = getattr(decision, "system", None)

            if system not in allowed_systems:

                self.logger.warning(
                    "Invalid system returned by "
                    f"DecisionAgent: {system}"
                )

                return self.contract_agent.to_decision_contract({
                    "system": "development",
                    "reason": (
                        "Invalid system returned by "
                        "decision model."
                    )
                })

            return self.contract_agent.to_decision_contract(decision)

        except Exception as error:

            self.logger.error(
                f"Decision error: {error}"
            )

            return self.contract_agent.to_decision_contract({
                "system": "chat",
                "reason": "fallback"
            })
