from agents.base_agent import BaseAgent

from app.core.logger import AppLogger





class MemoryAgent(BaseAgent):


    def __init__(
        self,
        memory
    ):


        super().__init__(
            "Memory Agent",
            memory
        )


        self.memory = memory

        self.logger = AppLogger()






    def save(
        self,
        message
    ):


        self.logger.info(
            f"Saving memory: {message}"
        )


        lower = message.lower()



        #
        # İsim kaydetme
        #

        if (
            "adım" in lower
            or
            "ismim" in lower
            or
            "benim adım" in lower
        ):


            name = self.extract_name(
                message
            )


            if name:


                self.memory.save(
                    "user_name",
                    name,
                    "personal"
                )


                return (
                    f"Tamam, adını {name} olarak hatırlayacağım."
                )



        #
        # Genel memory
        #

        self.memory.save(
            "last_memory",
            message,
            "general"
        )


        return (
            "Bilgi hafızaya kaydedildi."
        )









    def get(
        self,
        message
    ):


        self.logger.info(
            f"Getting memory: {message}"
        )


        lower = message.lower()



        try:


            #
            # İsim sorgusu
            #

            if (
                "adım ne" in lower
                or
                "ismim ne" in lower
                or
                "ben kimim" in lower
                or
                "adımı biliyor musun" in lower
            ):


                name = self.memory.get(
                    "user_name"
                )


                self.logger.info(
                    f"Retrieved name: {name}"
                )



                if name:


                    return (
                        f"Senin adın {name}."
                    )



                return (
                    "İsim bilgisi kayıtlı değil."
                )





            #
            # Genel memory getir
            #

            result = self.memory.get(
                "last_memory"
            )


            if result:


                return str(result)



            return (
                "Hatırlanan bilgi bulunamadı."
            )





        except Exception as error:


            self.logger.error(
                f"Memory get error: {error}"
            )


            return (
                f"Memory error: {error}"
            )









    def extract_name(
        self,
        message
    ):


        text = message.strip()



        patterns = [

            "benim adım",

            "adım",

            "ismim"

        ]



        lower = text.lower()



        for pattern in patterns:


            if pattern in lower:


                index = lower.find(
                    pattern
                )


                name = text[

                    index + len(pattern):

                ].strip()



                if name:


                    return name.capitalize()





        return None