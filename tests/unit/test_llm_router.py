import pytest

from models.llm_router import LLMRouter
from tests.fakes.fake_llm import FakeLLM


@pytest.mark.unit
def test_llm_router_has_model_returns_true_when_planner_has_model():
    planner = FakeLLM(model="planner-model")
    chat = FakeLLM(model="chat-model")
    router = LLMRouter(planner, chat)

    assert router.has_model("planner-model") is True


@pytest.mark.unit
def test_llm_router_has_model_returns_true_when_chat_has_model():
    planner = FakeLLM(model="planner-model")
    chat = FakeLLM(model="chat-model")
    router = LLMRouter(planner, chat)

    assert router.has_model("chat-model") is True


@pytest.mark.unit
def test_llm_router_has_model_returns_false_for_unknown_model():
    planner = FakeLLM(model="planner-model")
    chat = FakeLLM(model="chat-model")
    router = LLMRouter(planner, chat)

    assert router.has_model("unknown-model") is False


@pytest.mark.unit
def test_llm_router_has_model_returns_false_for_empty_model_name():
    planner = FakeLLM(model="planner-model")
    chat = FakeLLM(model="chat-model")
    router = LLMRouter(planner, chat)

    assert router.has_model("") is False


@pytest.mark.unit
def test_llm_router_has_model_handles_missing_planner_llm():
    chat = FakeLLM(model="chat-model")
    router = LLMRouter(None, chat)

    assert router.has_model("chat-model") is True


@pytest.mark.unit
def test_llm_router_has_model_handles_missing_chat_llm():
    planner = FakeLLM(model="planner-model")
    router = LLMRouter(planner, None)

    assert router.has_model("planner-model") is True


@pytest.mark.unit
def test_llm_router_has_model_returns_false_when_both_llms_are_missing():
    router = LLMRouter(None, None)

    assert router.has_model("any-model") is False