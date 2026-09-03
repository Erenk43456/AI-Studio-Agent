import pytest
import requests

from models.llm import LLM


class DummyConfig:

    model = "fake-model"
    endpoint = "http://localhost:11434"
    temperature = 0.3
    max_tokens = 2048
    timeout = 10


@pytest.mark.unit
def test_llm_initializes_from_config():

    llm = LLM(DummyConfig())

    assert llm.model == "fake-model"
    assert llm.base_url == "http://localhost:11434"
    assert llm.generate_url == (
        "http://localhost:11434/api/generate"
    )
    assert llm.temperature == 0.3
    assert llm.num_predict == 2048
    assert llm.request_timeout == 10


@pytest.mark.unit
def test_llm_normalizes_endpoint():

    config = DummyConfig()
    config.endpoint = (
        "http://localhost:11434/"
    )

    llm = LLM(config)

    assert llm.base_url == (
        "http://localhost:11434"
    )


@pytest.mark.unit
def test_llm_accepts_generate_endpoint():

    config = DummyConfig()
    config.endpoint = (
        "http://localhost:11434/api/generate"
    )

    llm = LLM(config)

    assert llm.generate_url == (
        "http://localhost:11434/api/generate"
    )

    assert llm.base_url == (
        "http://localhost:11434"
    )


@pytest.mark.unit
def test_llm_current_model():

    llm = LLM(DummyConfig())

    assert llm.get_current_model() == "fake-model"


@pytest.mark.unit
def test_llm_has_model(monkeypatch):

    llm = LLM(DummyConfig())

    monkeypatch.setattr(
        llm,
        "get_models",
        lambda: [
            "fake-model",
            "other-model",
        ],
    )

    assert llm.has_model("fake-model") is True


@pytest.mark.unit
def test_llm_missing_model(monkeypatch):

    llm = LLM(DummyConfig())

    monkeypatch.setattr(
        llm,
        "get_models",
        lambda: [
            "other-model",
        ],
    )

    assert llm.has_model("non-existent-model") is False


@pytest.mark.unit
def test_llm_connection_success(monkeypatch):

    llm = LLM(DummyConfig())

    class Response:

        status_code = 200

    monkeypatch.setattr(
        "models.llm.requests.get",
        lambda *args, **kwargs: Response(),
    )

    assert llm.check_connection() is True


@pytest.mark.unit
def test_llm_connection_failure(monkeypatch):

    llm = LLM(DummyConfig())

    class Response:

        status_code = 500

    monkeypatch.setattr(
        "models.llm.requests.get",
        lambda *args, **kwargs: Response(),
    )

    assert llm.check_connection() is False


@pytest.mark.unit
def test_llm_connection_exception(monkeypatch):

    llm = LLM(DummyConfig())

    def failing_get(*args, **kwargs):

        raise RuntimeError(
            "connection failed"
        )

    monkeypatch.setattr(
        "models.llm.requests.get",
        failing_get,
    )

    assert llm.check_connection() is False


@pytest.mark.unit
def test_llm_get_models(monkeypatch):

    llm = LLM(DummyConfig())

    class Response:

        def raise_for_status(self):
            pass

        def json(self):

            return {
                "models": [
                    {
                        "name": "qwen2.5:3b"
                    },
                    {
                        "name": "llama3:8b"
                    },
                ]
            }

    monkeypatch.setattr(
        "models.llm.requests.get",
        lambda *args, **kwargs: Response(),
    )

    assert llm.get_models() == [
        "qwen2.5:3b",
        "llama3:8b",
    ]


@pytest.mark.unit
def test_llm_get_models_failure(monkeypatch):

    llm = LLM(DummyConfig())

    def failing_get(*args, **kwargs):

        raise RuntimeError(
            "model list failed"
        )

    monkeypatch.setattr(
        "models.llm.requests.get",
        failing_get,
    )

    assert llm.get_models() == []


@pytest.mark.unit
def test_llm_generate_success(monkeypatch):

    llm = LLM(DummyConfig())

    class Response:

        def raise_for_status(self):
            pass

        def json(self):

            return {
                "response": "Hello from fake Ollama"
            }

    monkeypatch.setattr(
        "models.llm.requests.post",
        lambda *args, **kwargs: Response(),
    )

    result = llm.generate(
        "Hello"
    )

    assert result == "Hello from fake Ollama"


@pytest.mark.unit
def test_llm_generate_empty_response(monkeypatch):

    llm = LLM(DummyConfig())

    class Response:

        def raise_for_status(self):
            pass

        def json(self):

            return {
                "response": ""
            }

    monkeypatch.setattr(
        "models.llm.requests.post",
        lambda *args, **kwargs: Response(),
    )

    result = llm.generate(
        "Hello"
    )

    assert result == (
        "LLM_ERROR: Empty response."
    )


@pytest.mark.unit
def test_llm_generate_connection_failure(monkeypatch):

    llm = LLM(DummyConfig())

    def failing_post(*args, **kwargs):

        raise requests.exceptions.ConnectionError(
            "connection failed"
        )

    monkeypatch.setattr(
        "models.llm.requests.post",
        failing_post,
    )

    result = llm.generate(
        "Hello"
    )

    assert result == (
        "LLM_ERROR: "
        "Connection failed."
    )


@pytest.mark.unit
def test_llm_generate_does_not_run_separate_connection_check(
    monkeypatch,
):

    llm = LLM(DummyConfig())

    def fail_check_connection():

        raise AssertionError(
            "generate() must not call check_connection()"
        )

    monkeypatch.setattr(
        llm,
        "check_connection",
        fail_check_connection,
    )

    class FakeResponse:

        def raise_for_status(self):
            pass

        def json(self):

            return {
                "response": "generated"
            }

    monkeypatch.setattr(
        "models.llm.requests.post",
        lambda *args, **kwargs: FakeResponse(),
    )

    result = llm.generate(
        "hello"
    )

    assert result == "generated"