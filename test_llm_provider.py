from config.config_manager import ConfigManager
from models.llm_provider import LLMProvider


config = ConfigManager()


provider = LLMProvider(
    config
)


response = provider.generate(
    "Say hello in one sentence"
)


print(response)