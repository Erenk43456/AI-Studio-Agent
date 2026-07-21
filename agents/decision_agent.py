from agents.base_agent import BaseAgent


class DecisionAgent(BaseAgent):

    def __init__(self, registry):
        super().__init__("Decision Agent")
        self.registry = registry


    def process(self, request):

        request = request.lower()


        # İsim sorgu
        if "adım ne" in request:
            return "memory_get"


        # İsim kayıt
        if "benim adım" in request:

            name = request.replace("benim adım", "").strip()

            self.memory.save("isim", name)

            return "memory_save"


        # Öğrenme sorgu
        if "ne öğreniyorum" in request:
            return "memory_get_learning"


        # Öğrenme kayıt
        if "öğreniyorum" in request:

            value = request.replace("öğreniyorum", "").strip()

            value = value.replace("ben", "").strip()

            self.memory.save("öğreniyor", value)

            return "memory_save"


        # Favori oyun sorgu
        if "favori oyunum ne" in request:
            return "memory_get"


        # Favori oyun kayıt
        if "favori oyunum" in request:

            value = request.replace("benim favori oyunum", "").strip()

            self.memory.save("favori_oyun", value)

            return "memory_save"


        # Hesaplama
        if "topla" in request:
            return "calculator"


        if "çarp" in request:
            return "calculator"


        # Dosya
        if "dosya" in request or "oluştur" in request or "yaz" in request:
            return "file"


        return None