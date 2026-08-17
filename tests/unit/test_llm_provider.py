import pytest

from models.llm_provider import LLMProvider


class DummyConfig:

    name = "chat"
    model = "fake-model"
    provider = "local"
    endpoint = "http://localhost:11434"
    api_key = ""
    temperature = 0.3
    max_tokens = 2048
    timeout = 10


class FakeLLM:

    def __init__(self, config):

        self.config = config
        self.generate_calls = []

    def generate(
        self,
        prompt,
        max_tokens=None,
        temperature=None,
        timeout=None,
    ):

        self.generate_calls.append(
            {
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "timeout": timeout,
            }
        )

        return "fake response"

    def get_models(self):

        return [
            "fake-model",
            "other-model",
        ]

    def has_model(self):

        return True

    def check_connection(self):

        return True


@pytest.mark.unit
def test_provider_initializes_local(monkeypatch):

    monkeypatch.setattr(
        "models.llm_provider.LLM",
        FakeLLM,
    )

    provider = LLMProvider(
        DummyConfig()
    )

    assert isinstance(
        provider.llm,
        FakeLLM,
    )

    assert provider.model_slot == "chat"
    assert provider.current_model == "fake-model"


@pytest.mark.unit
def test_provider_generate(monkeypatch):

    monkeypatch.setattr(
        "models.llm_provider.LLM",
        FakeLLM,
    )

    provider = LLMProvider(
        DummyConfig()
    )

    result = provider.generate(
        "Hello",
        max_tokens=100,
        temperature=0.7,
        timeout=20,
    )

    assert result == "fake response"

    assert provider.llm.generate_calls == [
        {
            "prompt": "Hello",
            "max_tokens": 100,
            "temperature": 0.7,
            "timeout": 20,
        }
    ]


@pytest.mark.unit
def test_provider_get_models(monkeypatch):

    monkeypatch.setattr(
        "models.llm_provider.LLM",
        FakeLLM,
    )

    provider = LLMProvider(
        DummyConfig()
    )

    assert provider.get_models() == [
        "fake-model",
        "other-model",
    ]


@pytest.mark.unit
def test_provider_has_model(monkeypatch):

    monkeypatch.setattr(
        "models.llm_provider.LLM",
        FakeLLM,
    )

    provider = LLMProvider(
        DummyConfig()
    )

    assert provider.has_model() is True


@pytest.mark.unit
def test_provider_current_model(monkeypatch):

    monkeypatch.setattr(
        "models.llm_provider.LLM",
        FakeLLM,
    )

    provider = LLMProvider(
        DummyConfig()
    )

    assert provider.get_current_model() == (
        "fake-model"
    )


@pytest.mark.unit
def test_provider_connection(monkeypatch):

    monkeypatch.setattr(
        "models.llm_provider.LLM",
        FakeLLM,
    )

    provider = LLMProvider(
        DummyConfig()
    )

    assert provider.check_connection() is True