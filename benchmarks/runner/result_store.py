from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class BenchmarkResultStore:
    """Persists benchmark runs and aggregate statistics separately."""

    INCONCLUSIVE_ERROR_TYPES = {
        "TimeoutError",
        "ConnectionError",
        "Timeout",
        "APIError",
        "ProviderError",
        "ServerError",
    }

    INCONCLUSIVE_STATUS_CODES = {
        408,
        425,
        429,
        500,
        502,
        503,
        504,
        529,
    }

    def __init__(self, results_dir: Path):
        self.results_dir = results_dir
        self.results_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    # =========================================================
    # Paths
    # =========================================================

    def benchmark_dir(
        self,
        task_id: str,
    ) -> Path:

        path = self.results_dir / task_id

        path.mkdir(
            parents=True,
            exist_ok=True,
        )

        return path

    def runs_path(
        self,
        task_id: str,
    ) -> Path:

        return (
            self.benchmark_dir(task_id)
            / "runs.json"
        )

    def results_path(
        self,
        task_id: str,
    ) -> Path:

        return (
            self.benchmark_dir(task_id)
            / "results.json"
        )

    # =========================================================
    # Loading
    # =========================================================

    def _load_json(
        self,
        path: Path,
        default: Any,
    ) -> Any:

        if not path.exists():
            return default

        try:
            with path.open(
                "r",
                encoding="utf-8",
            ) as file:
                return json.load(file)

        except (
            json.JSONDecodeError,
            OSError,
        ):
            return default

    def load_runs(
        self,
        task_id: str,
    ) -> list[dict[str, Any]]:

        data = self._load_json(
            self.runs_path(task_id),
            {},
        )

        if not isinstance(data, dict):
            return []

        runs = data.get(
            "runs",
            [],
        )

        if not isinstance(runs, list):
            return []

        return [
            item
            for item in runs
            if isinstance(item, dict)
        ]

    # =========================================================
    # Classification
    # =========================================================

    def classify_run(
        self,
        result: dict[str, Any],
    ) -> str:
        """
        Return one of:

        PASS
        FAILURE
        INCONCLUSIVE
        """

        if result.get("success") is True:
            return "PASS"

        runtime_error = (
            result
            .get("validation", {})
            .get("runtime_error")
        )

        if runtime_error is None:
            runtime_error = (
                result
                .get("execution", {})
                .get("runtime_error")
            )

        if self._is_inconclusive_error(
            runtime_error
        ):
            return "INCONCLUSIVE"

        if self._contains_inconclusive_error(
            result
        ):
            return "INCONCLUSIVE"

        return "FAILURE"

    def _is_inconclusive_error(
        self,
        error: Any,
    ) -> bool:

        if not isinstance(
            error,
            dict,
        ):
            return False

        error_type = str(
            error.get(
                "type",
                "",
            )
        )

        message = str(
            error.get(
                "message",
                "",
            )
        ).lower()

        if error_type in self.INCONCLUSIVE_ERROR_TYPES:
            return True

        if self._contains_inconclusive_status(
            message
        ):
            return True

        inconclusive_keywords = (
            "api request error",
            "api error",
            "server error",
            "service unavailable",
            "provider unavailable",
            "provider error",
            "connection error",
            "connection reset",
            "connection refused",
            "timed out",
            "timeout",
            "rate limit",
            "too many requests",
            "http 408",
            "http 425",
            "http 429",
            "http 500",
            "http 502",
            "http 503",
            "http 504",
            "http 529",
            "503 server error",
            "502 bad gateway",
            "504 gateway timeout",
        )

        return any(
            keyword in message
            for keyword in inconclusive_keywords
        )

    def _contains_inconclusive_status(
        self,
        message: str,
    ) -> bool:

        for code in self.INCONCLUSIVE_STATUS_CODES:

            if str(code) in message:
                return True

        return False

    def _contains_inconclusive_error(
        self,
        result: dict[str, Any],
    ) -> bool:

        execution = result.get(
            "execution",
            {},
        )

        if isinstance(
            execution,
            dict,
        ):

            runtime_error = execution.get(
                "runtime_error"
            )

            if self._is_inconclusive_error(
                runtime_error
            ):
                return True

        validation = result.get(
            "validation",
            {},
        )

        if isinstance(
            validation,
            dict,
        ):

            runtime_error = validation.get(
                "runtime_error"
            )

            if self._is_inconclusive_error(
                runtime_error
            ):
                return True

            tests = validation.get(
                "tests",
                [],
            )

            if isinstance(
                tests,
                list,
            ):

                for test in tests:

                    if not isinstance(
                        test,
                        dict,
                    ):
                        continue

                    if self._is_inconclusive_error(
                        {
                            "type": test.get(
                                "error_type",
                                "",
                            ),
                            "message": test.get(
                                "error",
                                "",
                            ),
                        }
                    ):
                        return True

        return False

    # =========================================================
    # Failure information
    # =========================================================

    def failure_info(
        self,
        result: dict[str, Any],
        status: str,
    ) -> dict[str, Any] | None:

        if status not in {
            "FAILURE",
            "INCONCLUSIVE",
        }:
            return None

        cause = self._extract_cause(
            result
        )

        return {
            "cause": cause,
            "error_type": self._extract_error_type(
                result
            ),
        }

    def _extract_cause(
        self,
        result: dict[str, Any],
    ) -> str:

        validation = result.get(
            "validation",
            {},
        )

        if isinstance(
            validation,
            dict,
        ):

            runtime_error = validation.get(
                "runtime_error"
            )

            if isinstance(
                runtime_error,
                dict,
            ):

                message = runtime_error.get(
                    "message"
                )

                if message:
                    return str(message)

            tests = validation.get(
                "tests",
                [],
            )

            if isinstance(
                tests,
                list,
            ):

                errors = []

                for test in tests:

                    if not isinstance(
                        test,
                        dict,
                    ):
                        continue

                    error = test.get(
                        "error"
                    )

                    if error:
                        errors.append(
                            str(error)
                        )

                if errors:
                    return "; ".join(errors)

        execution = result.get(
            "execution",
            {},
        )

        if isinstance(
            execution,
            dict,
        ):

            runtime_error = execution.get(
                "runtime_error"
            )

            if isinstance(
                runtime_error,
                dict,
            ):

                message = runtime_error.get(
                    "message"
                )

                if message:
                    return str(message)

        agent_result = result.get(
            "agent_result"
        )

        if isinstance(
            agent_result,
            dict,
        ):

            error = agent_result.get(
                "error"
            )

            if error:
                return str(error)

        return "Unknown benchmark failure"

    def _extract_error_type(
        self,
        result: dict[str, Any],
    ) -> str | None:

        validation = result.get(
            "validation",
            {},
        )

        if isinstance(
            validation,
            dict,
        ):

            runtime_error = validation.get(
                "runtime_error"
            )

            if isinstance(
                runtime_error,
                dict,
            ):

                error_type = runtime_error.get(
                    "type"
                )

                if error_type:
                    return str(error_type)

            tests = validation.get(
                "tests",
                [],
            )

            if isinstance(
                tests,
                list,
            ):

                for test in tests:

                    if not isinstance(
                        test,
                        dict,
                    ):
                        continue

                    error_type = test.get(
                        "error_type"
                    )

                    if error_type:
                        return str(error_type)

        execution = result.get(
            "execution",
            {},
        )

        if isinstance(
            execution,
            dict,
        ):

            runtime_error = execution.get(
                "runtime_error"
            )

            if isinstance(
                runtime_error,
                dict,
            ):

                error_type = runtime_error.get(
                    "type"
                )

                if error_type:
                    return str(error_type)

        return None

    # =========================================================
    # Agent / model extraction
    # =========================================================

    def extract_agents(
        self,
        result: dict[str, Any],
    ) -> dict[str, str | None]:

        execution = result.get(
            "execution",
            {},
        )

        if not isinstance(
            execution,
            dict,
        ):
            return {}

        agents = execution.get(
            "agents",
            {},
        )

        if not isinstance(
            agents,
            dict,
        ):
            return {}

        output: dict[str, str | None] = {}

        for name, data in agents.items():

            if not isinstance(
                data,
                dict,
            ):
                continue

            output[str(name)] = (
                data.get("model")
            )

        return output

    def extract_models(
        self,
        result: dict[str, Any],
    ) -> dict[str, str]:

        models = result.get(
            "models",
            {},
        )

        if not isinstance(
            models,
            dict,
        ):
            return {}

        return {
            str(agent): str(model)
            for agent, model in models.items()
            if model
        }

    # =========================================================
    # Run persistence
    # =========================================================

    def save_run(
        self,
        task_id: str,
        result: dict[str, Any],
    ) -> dict[str, Any]:

        runs = self.load_runs(
            task_id
        )

        run_id = len(runs) + 1

        status = self.classify_run(
            result
        )

        failure = self.failure_info(
            result,
            status,
        )

        run = {
            "run_id": run_id,
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "status": status,

            "changed_files": result.get(
                "changed_files",
                [],
            ),

            "validation": result.get(
                "validation",
                {},
            ),

            "agents": self.extract_agents(
                result
            ),

            "models": self.extract_models(
                result
            ),
        }

        if failure is not None:

            run["failure"] = {
                "cause": failure["cause"],
                "error_type": failure["error_type"],
            }

        runs.append(run)

        payload = {
            "meta": {
                "id": result.get(
                    "id",
                    task_id,
                ),
                "name": result.get(
                    "name",
                    task_id,
                ),
                "total_runs": len(runs),
            },
            "runs": runs,
        }

        self._write_json(
            self.runs_path(task_id),
            payload,
        )

        return run

    # =========================================================
    # Aggregate statistics
    # =========================================================

    def rebuild_results(
        self,
        task_id: str,
        result: dict[str, Any],
    ) -> dict[str, Any]:

        runs = self.load_runs(
            task_id
        )

        benchmark = self._empty_bucket()

        agents: dict[str, dict[str, Any]] = {}

        models: dict[str, dict[str, Any]] = {}

        agent_models: dict[str, dict[str, Any]] = {}

        for run in runs:

            run_id = run.get(
                "run_id"
            )

            status = run.get(
                "status"
            )

            run_agents = run.get(
                "agents",
                {},
            )

            if isinstance(
                run_agents,
                dict,
            ):

                for agent_name, model in run_agents.items():

                    agent_name = str(agent_name)

                    self._ensure_stat_bucket(
                        agents,
                        agent_name,
                    )

                    self._update_attribution(
                        agents[agent_name],
                        run,
                    )

                    if model:

                        model = str(model)

                        key = (
                            f"{agent_name}@{model}"
                        )

                        self._ensure_stat_bucket(
                            agent_models,
                            key,
                        )

                        self._update_attribution(
                            agent_models[key],
                            run,
                        )

                        self._ensure_stat_bucket(
                            models,
                            model,
                        )

                        self._update_attribution(
                            models[model],
                            run,
                        )

            if not isinstance(
                run_id,
                int,
            ):
                continue

            if status == "PASS":

                benchmark["passed"].append(
                    run_id
                )

            elif status == "FAILURE":

                benchmark["failures"].append(
                    {
                        "run_id": run_id,
                        "cause": (
                            run.get(
                                "failure",
                                {},
                            ).get(
                                "cause",
                                "Unknown failure",
                            )
                        ),
                    }
                )

            elif status == "INCONCLUSIVE":

                benchmark["inconclusive"].append(
                    {
                        "run_id": run_id,
                        "cause": (
                            run.get(
                                "failure",
                                {},
                            ).get(
                                "cause",
                                "Unknown inconclusive error",
                            )
                        ),
                    }
                )

        # -----------------------------------------------------
        # Final document
        # -----------------------------------------------------

        payload = {
            "meta": {
                "id": result.get(
                    "id",
                    task_id,
                ),
                "name": result.get(
                    "name",
                    task_id,
                ),
                "total_runs": len(runs),
                "passed_runs": len(
                    benchmark["passed"]
                ),
                "failed_runs": len(
                    benchmark["failures"]
                ),
                "inconclusive_runs": len(
                    benchmark["inconclusive"]
                ),
                "pass_rate": self._rate(
                    len(benchmark["passed"]),
                    len(runs)
                    - len(benchmark["inconclusive"]),
                ),
                "fail_rate": self._rate(
                    len(benchmark["failures"]),
                    len(runs)
                    - len(benchmark["inconclusive"]),
                ),
            },
            "benchmark": benchmark,
            "agents": agents,
            "models": models,
            "agent_model": agent_models,
        }

        self._write_json(
            self.results_path(task_id),
            payload,
        )

        return payload

    # =========================================================
    # Attribution helpers
    # =========================================================

    def _empty_bucket(
        self,
    ) -> dict[str, Any]:

        return {
            "passed": [],
            "failures": [],
            "inconclusive": [],
        }

    def _ensure_stat_bucket(
        self,
        mapping: dict[str, dict[str, Any]],
        key: str,
    ) -> None:

        if key not in mapping:

            mapping[key] = {
                "total": 0,
                "passed": [],
                "failures": [],
                "inconclusive": [],
                "pass_rate": 0.0,
                "failure_rate": 0.0,
                "inconclusive_rate": 0.0,
            }

    def _update_attribution(
        self,
        bucket: dict[str, Any],
        run: dict[str, Any],
        model: Any = None,
    ) -> None:

        run_id = run.get(
            "run_id"
        )

        if not isinstance(
            run_id,
            int,
        ):
            return

        status = run.get(
            "status"
        )

        bucket["total"] += 1

        if status == "PASS":

            bucket["passed"].append(
                run_id
            )

        elif status == "FAILURE":

            failure = run.get(
                "failure",
                {},
            )

            bucket["failures"].append(
                {
                    "run_id": run_id,
                    "cause": (
                        failure.get(
                            "cause",
                            "Unknown failure",
                        )
                        if isinstance(
                            failure,
                            dict,
                        )
                        else "Unknown failure"
                    ),
                }
            )

        elif status == "INCONCLUSIVE":

            failure = run.get(
                "failure",
                {},
            )

            bucket["inconclusive"].append(
                {
                    "run_id": run_id,
                    "cause": (
                        failure.get(
                            "cause",
                            "Unknown inconclusive error",
                        )
                        if isinstance(
                            failure,
                            dict,
                        )
                        else "Unknown inconclusive error"
                    ),
                }
            )

        denominator = (
            bucket["total"]
            - len(
                bucket["inconclusive"]
            )
        )

        bucket["pass_rate"] = self._rate(
            len(bucket["passed"]),
            denominator,
        )

        bucket["failure_rate"] = self._rate(
            len(bucket["failures"]),
            denominator,
        )

        bucket["inconclusive_rate"] = self._rate(
            len(bucket["inconclusive"]),
            bucket["total"],
        )

    @staticmethod
    def _rate(
        numerator: int,
        denominator: int,
    ) -> float:

        if denominator <= 0:
            return 0.0

        return round(
            (numerator / denominator) * 100,
            2,
        )

    # =========================================================
    # IO
    # =========================================================

    def _write_json(
        self,
        path: Path,
        payload: dict[str, Any],
    ) -> None:

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                payload,
                file,
                indent=2,
                ensure_ascii=False,
            )