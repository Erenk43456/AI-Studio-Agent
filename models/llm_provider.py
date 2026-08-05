from models.llm import LLM
from models.api_llm import APILLM



class LLMProvider:


    def __init__(
        self,
        config,
        model_slot
    ):


        provider = config.get(
            "llm_provider",
            "local"
        )


        self.model_slot = model_slot


        self.current_model = config.get(
            model_slot,
            None
        )



        if provider == "api":


            api_config = {


                "api_url":

                config.get(
                    "api_url",
                    ""
                ),



                "api_key":

                config.get(
                    "api_key",
                    ""
                ),



                "api_model":

                self.current_model,



                "temperature":

                config.get(
                    "temperature",
                    0.3
                ),



                "api_timeout":

                config.get(
                    "api_timeout",
                    120
                ),



                "num_predict":

                config.get(
                    "num_predict",
                    1200
                )

            }



            self.llm = APILLM(
                api_config
            )



        else:


            self.llm = LLM(
                config
            )





    def generate(
        self,
        prompt,
        max_tokens=None,
        temperature=None,
        timeout=None
    ):


        return self.llm.generate(

            prompt,

            max_tokens=max_tokens,

            temperature=temperature,

            timeout=timeout

        )





    def get_models(self):


        if hasattr(
            self.llm,
            "get_models"
        ):

            return self.llm.get_models()


        return [
            self.current_model
        ]





    def has_model(self):


        return self.current_model is not None





    def get_current_model(self):


        return self.current_model





    def check_connection(self):


        if hasattr(
            self.llm,
            "check_connection"
        ):

            return self.llm.check_connection()


        return False