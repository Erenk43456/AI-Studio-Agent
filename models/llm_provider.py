from models.llm import LLM
from models.api_llm import APILLM



class LLMProvider:


    def __init__(self, config):


        provider = config.get(
            "llm_provider",
            "local"
        )


        if provider == "api":

            self.llm = APILLM()

        else:

            self.llm = LLM()





    def generate(
        self,
        prompt
    ):

        return self.llm.generate(
            prompt
        )





    def get_models(self):

        if hasattr(
            self.llm,
            "get_models"
        ):

            return self.llm.get_models()

        return []





    def has_model(self):

        if hasattr(
            self.llm,
            "has_model"
        ):

            return self.llm.has_model()

        return False





    def get_current_model(self):

        if hasattr(
            self.llm,
            "get_current_model"
        ):

            return self.llm.get_current_model()

        return None





    def check_connection(self):

        if hasattr(
            self.llm,
            "check_connection"
        ):

            return self.llm.check_connection()

        return False