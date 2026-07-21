from agents.base_agent import BaseAgent


class DecisionAgent(BaseAgent):

    def __init__(self, memory):
        super().__init__("Decision Agent")
        self.memory = memory


    def process(self, request):

        request = request.lower().strip()


        # İsim sorgu
        if "adım ne" in request:
            return "memory_get"


        # İsim kayıt
        if "benim adım" in request:

            name = request.replace(
                "benim adım",
                ""
            ).strip()

            if name:
                self.memory.save(
                    "isim",
                    name
                )

            return "memory_save"


        # Öğrenme sorgu
        if "ne öğreniyorum" in request:
            return "memory_get_learning"


        # Öğrenme kayıt
        if "öğreniyorum" in request:

            value = request.replace(
                "öğreniyorum",
                ""
            ).replace(
                "ben",
                ""
            ).strip()


            if value:
                self.memory.save(
                    "öğreniyor",
                    value
                )

            return "memory_save"


        # Favori oyun sorgu
        if "favori oyunum ne" in request:
            return "memory_get"


        # Favori oyun kayıt
        if "favori oyunum" in request:

            value = request.replace(
                "benim favori oyunum",
                ""
            ).strip()


            if value:
                self.memory.save(
                    "favori_oyun",
                    value
                )

            return "memory_save"


        # Hesaplama
        calculation_words = [
            "topla",
            "çıkar",
            "çarp",
            "böl"
        ]


        if any(
            word in request
            for word in calculation_words
        ):
            return "calculator"


        # Dosya işlemleri
        file_words = [
            "dosya",
            "oluştur",
            "yaz"
        ]


        if any(
            word in request
            for word in file_words
        ):
            return "file"


        return None