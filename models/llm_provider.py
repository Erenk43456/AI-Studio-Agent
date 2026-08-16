from models.llm import LLM
from models.api_llm import APILLM


class LLMProvider:

    def __init__(
        self,
        model_config
    ):

        self.config = model_config

        self.model_slot = (
            model_config.name
        )

        self.current_model = (
            model_config.model
        )

        provider = (
            model_config.provider
            .lower()
            .strip()
        )

        if provider == "api":

            self.llm = APILLM(
                model_config
            )

        else:

            self.llm = LLM(
                model_config
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


    def get_models(
        self
    ):

        if hasattr(
            self.llm,
            "get_models"
        ):

            return self.llm.get_models()

        return [
            self.current_model
        ] if self.current_model else []


    def has_model(
        self
    ):

        if hasattr(
            self.llm,
            "has_model"
        ):

            return self.llm.has_model()

        return bool(
            self.current_model
        )


    def get_current_model(
        self
    ):

        return self.current_model


    def check_connection(
        self
    ):

        if hasattr(
            self.llm,
            "check_connection"
        ):

            return self.llm.check_connection()

        return False