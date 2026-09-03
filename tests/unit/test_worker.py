import pytest

from app.worker import AIWorker


@pytest.mark.unit
def test_ai_worker_creates_cancel_event():

    worker = AIWorker(
        orchestrator=None,
        conversation=None,
        message="hello",
    )

    assert worker.cancel_event.is_set() is False


@pytest.mark.unit
def test_ai_worker_stop_sets_cancel_event():

    worker = AIWorker(
        orchestrator=None,
        conversation=None,
        message="hello",
    )

    worker.stop()

    assert worker.cancel_event.is_set() is True