from abc import ABC, abstractmethod


class LLMContract(ABC):
    """
    Contract interface that all LLM providers in AI-Studio must satisfy.
    """

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate a response text for the given prompt."""
        pass

    @abstractmethod
    def check_connection(self) -> bool:
        """Check if connection to the LLM provider is active."""
        pass

    @abstractmethod
    def get_current_model(self) -> str:
        """Return current model name."""
        pass

    @abstractmethod
    def get_models(self) -> list:
        """Return available model names."""
        pass

    @abstractmethod
    def has_model(self, model_name: str) -> bool:
        """Check if specified model is available."""
        pass
