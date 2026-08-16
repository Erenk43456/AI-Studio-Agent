from dataclasses import dataclass


@dataclass
class ModelConfig:

    name: str

    provider: str

    model: str

    endpoint: str

    api_key: str = ""

    temperature: float = 0.3

    max_tokens: int = 2048

    timeout: int = 120

    enabled: bool = True

    def to_dict(self):

        return {
            "name": self.name,
            "provider": self.provider,
            "model": self.model,
            "endpoint": self.endpoint,
            "api_key": self.api_key,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
            "enabled": self.enabled
        }
