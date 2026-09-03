import threading

import pytest
import requests

from models.api_llm import APILLM


class DummyConfig:

    model = "fake-model"
    endpoint = "https://example.com/v1/chat/completions"
    api_key = ""
    temperature = 0.3
    max_tokens = 2048
    timeout = 10
    max_retries = 3
    retry_backoff = 2


@pytest.mark.unit
def test_api_llm_generate_success(monkeypatch):

    llm = APILLM(
        DummyConfig()
    )

    class Response:

        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):

            return {
                "choices": [
                    {
                        "message": {
                            "content": "Hello"
                        }
                    }
                ]
            }

    monkeypatch.setattr(
        "models.api_llm.requests.post",
        lambda *args, **kwargs: Response(),
    )

    result = llm.generate(
        "Hello"
    )

    assert result == "Hello"


@pytest.mark.unit
def test_api_llm_generate_retries_timeout(monkeypatch):

    config = DummyConfig()
    config.max_retries = 2

    llm = APILLM(
        config
    )

    calls = []

    class Response:

        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):

            return {
                "choices": [
                    {
                        "message": {
                            "content": "Recovered"
                        }
                    }
                ]
            }

    def fake_post(*args, **kwargs):

        calls.append(1)

        if len(calls) == 1:

            raise requests.exceptions.Timeout(
                "timeout"
            )

        return Response()

    monkeypatch.setattr(
        "models.api_llm.requests.post",
        fake_post,
    )

    monkeypatch.setattr(
        "models.api_llm.time.sleep",
        lambda *args, **kwargs: None,
    )

    result = llm.generate(
        "Hello"
    )

    assert result == "Recovered"
    assert len(calls) == 2


@pytest.mark.unit
def test_api_llm_generate_cancellation_before_request(
    monkeypatch,
):

    llm = APILLM(
        DummyConfig()
    )

    cancel_event = threading.Event()
    cancel_event.set()

    def fail_post(*args, **kwargs):

        raise AssertionError(
            "HTTP request must not start after cancellation."
        )

    monkeypatch.setattr(
        "models.api_llm.requests.post",
        fail_post,
    )

    result = llm.generate(
        "Hello",
        cancel_event=cancel_event,
    )

    assert result == {
        "error": "API request cancelled."
    }


@pytest.mark.unit
def test_api_llm_generate_cancellation_after_retryable_error(
    monkeypatch,
):

    llm = APILLM(
        DummyConfig()
    )

    cancel_event = threading.Event()
    calls = []

    class Response:

        status_code = 500

        def raise_for_status(self):
            raise requests.exceptions.HTTPError(
                "server error"
            )

    def fake_post(*args, **kwargs):

        calls.append(1)
        cancel_event.set()

        return Response()

    monkeypatch.setattr(
        "models.api_llm.requests.post",
        fake_post,
    )

    result = llm.generate(
        "Hello",
        cancel_event=cancel_event,
    )

    assert result == {
        "error": "API request cancelled."
    }

    assert len(calls) == 1