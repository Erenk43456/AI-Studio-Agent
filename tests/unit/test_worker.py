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

@pytest.mark.unit
def test_ai_worker_propagates_cancel_event_to_model_container():

    class FakeModels:

        def __init__(self):
            self.cancel_event = None

        def set_cancel_event(self, cancel_event):
            self.cancel_event = cancel_event

    class FakeContainer:

        def __init__(self):
            self.models = FakeModels()

    class FakeOrchestrator:

        def __init__(self):
            self.container = FakeContainer()

    orchestrator = FakeOrchestrator()

    worker = AIWorker(
        orchestrator=orchestrator,
        conversation=None,
        message="hello",
    )

    assert (
        orchestrator.container.models.cancel_event
        is worker.cancel_event
    )

    worker.stop()

    assert (
        orchestrator.container.models.cancel_event.is_set()
        is True
    )