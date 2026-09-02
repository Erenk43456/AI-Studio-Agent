import pytest

from tests.fakes.fake_model_provider import FakeModelProvider
from contracts.llm_contract import LLMContract


@pytest.mark.contract
def test_model_provider_satisfies_llm_contract():
    provider = FakeModelProvider()
    assert isinstance(provider, LLMContract)


@pytest.mark.contract
def test_model_provider_has_generate():


    provider = FakeModelProvider()

    assert callable(
        provider.generate
    )


@pytest.mark.contract
def test_model_provider_generate_returns_string():

    provider = FakeModelProvider(
        response="contract response"
    )

    result = provider.generate(
        "hello"
    )

    assert isinstance(
        result,
        str,
    )

    assert result == (
        "contract response"
    )


@pytest.mark.contract
def test_model_provider_tracks_generate_calls():

    provider = FakeModelProvider()

    provider.generate(
        "first"
    )

    provider.generate(
        "second"
    )

    assert len(
        provider.calls
    ) == 2

    assert provider.calls == [
        "first",
        "second",
    ]


@pytest.mark.contract
def test_model_provider_has_connection_check():

    provider = FakeModelProvider()

    assert callable(
        provider.check_connection
    )

    assert provider.check_connection() is True


@pytest.mark.contract
def test_model_provider_exposes_current_model():

    provider = FakeModelProvider(
        model="contract-model"
    )

    assert (
        provider.get_current_model()
        == "contract-model"
    )


@pytest.mark.contract
def test_model_provider_exposes_models():

    provider = FakeModelProvider(
        model="contract-model"
    )

    models = provider.get_models()

    assert isinstance(
        models,
        list,
    )

    assert "contract-model" in models


@pytest.mark.contract
def test_model_provider_can_check_model():

    provider = FakeModelProvider(
        model="contract-model"
    )

    assert provider.has_model(
        "contract-model"
    ) is True

    assert provider.has_model(
        "other-model"
    ) is False