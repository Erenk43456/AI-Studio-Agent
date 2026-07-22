from agents.base_agent import BaseAgent



class DecisionAgent(BaseAgent):


    def __init__(self, memory):

        super().__init__(
            "Decision Agent"
        )

        self.memory = memory





    def process(self, request):


        request = request.lower().strip()





        #
        # Name query
        #

        if (
            "adım ne" in request
            or "ismim ne" in request
            or "ben kimim" in request
        ):

            return "memory_get"







        #
        # Name storage
        #

        if "benim adım" in request:


            return "memory_save"








        #
        # Learning query
        #

        if "ne öğreniyorum" in request:


            return "memory_get_learning"








        #
        # Learning storage
        #

        if (
            "öğreniyorum" in request
            or "ogreniyorum" in request
        ):


            return "memory_save"








        #
        # Favorite game query
        #

        if "favori oyunum ne" in request:


            return "memory_get"








        #
        # Favorite game storage
        #

        if "favori oyunum" in request:


            return "memory_save"









        #
        # Calculator detection
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



        if any(

            word in request

            for word in calculation_words

        ):


            return "calculator"









        #
        # File operation detection
        #

        file_words = [

            "dosya",
            "oluştur",
            "olustur",
            "yaz"

        ]



        if any(

            word in request

            for word in file_words

        ):


            return "file"









        return None