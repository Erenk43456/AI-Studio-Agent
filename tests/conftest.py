"""
Shared pytest configuration and fixtures for AI-Studio-Agent.

This module intentionally contains only test-infrastructure concerns.
Application-specific fixtures should live in the appropriate test package.
"""


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "unit: fast isolated unit tests",
    )
    config.addinivalue_line(
        "markers",
        "contract: architecture and interface contract tests",
    )
    config.addinivalue_line(
        "markers",
        "integration: multi-component integration tests",
    )
    config.addinivalue_line(
        "markers",
        "e2e: end-to-end application workflow tests",
    )
    config.addinivalue_line(
        "markers",
        "benchmark: evaluation and benchmark tests",
    )
    config.addinivalue_line(
        "markers",
        "slow: slow-running tests",
    )
    config.addinivalue_line(
        "markers",
        "network: tests requiring network access",
    )
    config.addinivalue_line(
        "markers",
        "llm: tests requiring a real LLM",
    )

import pytest

from tests.fakes.fake_llm import FakeLLM
from tests.fakes.fake_memory import FakeMemory
from tests.fakes.fake_model_provider import FakeModelProvider
from tests.fakes.fake_tool import FakeTool


@pytest.fixture
def fake_llm():
    return FakeLLM()


@pytest.fixture
def fake_model_provider():
    return FakeModelProvider()


@pytest.fixture
def fake_memory():
    return FakeMemory()


@pytest.fixture
def fake_tool():
    return FakeTool()