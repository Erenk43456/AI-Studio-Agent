import logging

import pytest

from app.core.logger import AppLogger


@pytest.mark.unit
def test_app_logger_does_not_duplicate_handlers():
    logger = logging.getLogger("AI-Studio-Agent")

    logger.handlers.clear()

    first = AppLogger()
    second = AppLogger()

    assert first.logger is second.logger
    assert len(second.logger.handlers) == 2