from __future__ import annotations

import json
from pathlib import Path

import pytest

from benchmarks.runner.benchmark_runner import BenchmarkRunner


TASKS_DIR = (
    Path(__file__).resolve().parents[2]
    / "benchmarks"
    / "tasks"
)


def discover_benchmark_tasks() -> list[str]:
    """Discover all benchmark task IDs from benchmark task files."""

    if not TASKS_DIR.exists():
        return []

    return sorted(
        path.stem
        for path in TASKS_DIR.glob("*.json")
        if path.is_file()
    )


BENCHMARK_TASKS = discover_benchmark_tasks()


@pytest.mark.benchmark
@pytest.mark.llm
@pytest.mark.network
@pytest.mark.parametrize(
    "task_id",
    BENCHMARK_TASKS,
)
def test_benchmark(task_id: str) -> None:
    """Run a benchmark task and assert that it succeeds."""

    runner = BenchmarkRunner()

    result = runner.run(task_id)

    validation = json.dumps(
        result["validation"],
        indent=2,
        ensure_ascii=False,
    )

    assert result["success"], (
        f"\n\n"
        f"Benchmark failed: {task_id}\n"
        f"Agent result: {result['agent_result']}\n"
        f"Changed files: {result['changed_files']}\n"
        f"Validation:\n{validation}"
    )


def test_benchmark_tasks_exist() -> None:
    """Ensure that the benchmark suite contains at least one task."""

    assert BENCHMARK_TASKS, (
        f"No benchmark tasks found in {TASKS_DIR}"
    )