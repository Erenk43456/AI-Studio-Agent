from models.llm import LLM
from models.api_llm import APILLM

from contracts.llm_contract import LLMContract


class LLMProvider(LLMContract):

    def __init__(
        self,
        model_config,
        agent_name=None
    ):

        self.config = model_config

        self.agent_name = agent_name

        self.model_slot = model_config.name

        self.current_model = (
            model_config.model
        )

        self.cancel_event = None

        provider = (
            model_config.provider
            or "local"
        ).lower()

        if provider == "api":

            self.llm = APILLM(
                model_config,
                agent_name=self.agent_name
            )

        else:

            self.llm = LLM(
                model_config
            )

    # =========================================================
    # GENERATE
    # =========================================================

    def generate(
        self,
        prompt,
        max_tokens=None,
        temperature=None,
        timeout=None,
        cancel_event=None
    ):

        return self.llm.generate(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=timeout,
            cancel_event=(
                cancel_event
                if cancel_event is not None
                else self.cancel_event
            )
        )

    def set_cancel_event(
        self,
        cancel_event
    ):
        self.cancel_event = cancel_event

    # =========================================================
    # MODELS
    # =========================================================

    def get_models(self):

        if hasattr(
            self.llm,
            "get_models"
        ):

            return self.llm.get_models()

        return [
            self.current_model
        ]

    # =========================================================
    # MODEL
    # =========================================================

    def has_model(
        self,
        model_name: str
    ) -> bool:

        if hasattr(
            self.llm,
            "has_model"
        ):

            return self.llm.has_model(model_name)

        return bool(
            model_name
        )

    def get_current_model(self):

        return self.current_model

    # =========================================================
    # CONNECTION
    # =========================================================

    def check_connection(self):

        if hasattr(
            self.llm,
            "check_connection"
        ):

            return self.llm.check_connection()

        return False