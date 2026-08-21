from __future__ import annotations

import json
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.containers.main_container import MainContainer


class BenchmarkRunner:
    """Runs AI-Studio benchmark tasks in isolated workspaces."""

    IGNORED_PATHS = {
        ".ai_memory",
    }

    def __init__(
        self,
        project_root: Path | None = None,
    ):
        self.project_root = (
            project_root
            if project_root is not None
            else Path.cwd()
        ).resolve()

        self.tasks_dir = (
            self.project_root
            / "benchmarks"
            / "tasks"
        )

        self.results_dir = (
            self.project_root
            / "benchmarks"
            / "results"
        )

        self.results_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    # =========================================================
    # Task
    # =========================================================

    def load_task(
        self,
        task_id: str,
    ) -> dict[str, Any]:

        task_path = (
            self.tasks_dir
            / f"{task_id}.json"
        )

        if not task_path.exists():
            raise FileNotFoundError(
                f"Benchmark task not found: {task_path}"
            )

        with task_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    # =========================================================
    # Workspace
    # =========================================================

    def create_workspace(self) -> Path:

        return Path(
            tempfile.mkdtemp(
                prefix="ai-studio-benchmark-"
            )
        )

    def setup_workspace(
        self,
        workspace: Path,
        task: dict[str, Any],
    ) -> None:

        setup = task.get(
            "setup",
            {},
        )

        if not isinstance(
            setup,
            dict,
        ):
            return

        files = setup.get(
            "files",
            {},
        )

        if not isinstance(
            files,
            dict,
        ):
            return

        workspace_path = workspace.resolve()

        for filename, content in files.items():

            if not isinstance(
                filename,
                str,
            ):
                continue

            if not isinstance(
                content,
                str,
            ):
                continue

            path = (
                workspace_path
                / filename
            ).resolve()

            try:
                path.relative_to(
                    workspace_path
                )
            except ValueError:
                raise ValueError(
                    "Benchmark setup path is outside "
                    f"workspace: {filename}"
                )

            path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            path.write_text(
                content,
                encoding="utf-8",
            )

    # =========================================================
    # Snapshots
    # =========================================================

    def snapshot_files(
        self,
        workspace: Path,
    ) -> set[str]:

        files: set[str] = set()

        for path in workspace.rglob("*"):

            if not path.is_file():
                continue

            relative = path.relative_to(
                workspace
            )

            if (
                relative.parts
                and relative.parts[0]
                in self.IGNORED_PATHS
            ):
                continue

            files.add(
                str(relative)
            )

        return files

    def snapshot_file_contents(
        self,
        workspace: Path,
    ) -> dict[str, str]:

        snapshot: dict[str, str] = {}

        for path in workspace.rglob("*"):

            if not path.is_file():
                continue

            relative = path.relative_to(
                workspace
            )

            if (
                relative.parts
                and relative.parts[0]
                in self.IGNORED_PATHS
            ):
                continue

            try:
                snapshot[str(relative)] = (
                    path.read_text(
                        encoding="utf-8"
                    )
                )
            except (
                UnicodeDecodeError,
                OSError,
            ):
                continue

        return snapshot

    def detect_changed_files(
        self,
        before_files: set[str],
        after_files: set[str],
        before_contents: dict[str, str],
        after_contents: dict[str, str],
    ) -> set[str]:

        created = (
            after_files
            - before_files
        )

        deleted = (
            before_files
            - after_files
        )

        modified = {
            filename
            for filename in (
                before_files
                & after_files
            )
            if (
                before_contents.get(filename)
                != after_contents.get(filename)
            )
        }

        return (
            created
            | deleted
            | modified
        )

    # =========================================================
    # Models
    # =========================================================

    def collect_models(
        self,
        container: MainContainer | None,
        execution: dict[str, Any] | None,
    ) -> dict[str, Any]:

        models: dict[str, Any] = {}

        if isinstance(
            execution,
            dict,
        ):

            execution_models = execution.get(
                "models",
                {},
            )

            if isinstance(
                execution_models,
                dict,
            ):

                for name, model in execution_models.items():

                    if model:
                        models[name] = model

            agents = execution.get(
                "agents",
                {},
            )

            if isinstance(
                agents,
                dict,
            ):

                for name, agent_data in agents.items():

                    if not isinstance(
                        agent_data,
                        dict,
                    ):
                        continue

                    model = agent_data.get(
                        "model"
                    )

                    if model:
                        models[name] = model

        if container is not None:

            container_models = getattr(
                container,
                "models",
                None,
            )

            if container_models is not None:

                model_mapping = {
                    "chat": "chat_llm",
                    "code": "code_llm",
                    "planner": "planner_llm",
                    "decision": "decision_llm",
                }

                for name, attribute in model_mapping.items():

                    if name in models:
                        continue

                    llm = getattr(
                        container_models,
                        attribute,
                        None,
                    )

                    if llm is None:
                        continue

                    getter = getattr(
                        llm,
                        "get_current_model",
                        None,
                    )

                    if not callable(getter):
                        continue

                    try:

                        model = getter()

                    except Exception:
                        continue

                    if model:
                        models[name] = model

        return models

    # =========================================================
    # Execution
    # =========================================================

    def normalize_execution(
        self,
        execution: Any,
    ) -> dict[str, Any]:

        if not isinstance(
            execution,
            dict,
        ):
            return {
                "agents": {},
                "models": {},
            }

        agents = execution.get(
            "agents",
            {},
        )

        models = execution.get(
            "models",
            {},
        )

        if not isinstance(
            agents,
            dict,
        ):
            agents = {}

        if not isinstance(
            models,
            dict,
        ):
            models = {}

        return {
            "agents": agents,
            "models": models,
        }

    # =========================================================
    # Run
    # =========================================================

    def run(
        self,
        task_id: str,
    ) -> dict[str, Any]:

        task = self.load_task(
            task_id
        )

        workspace = self.create_workspace()

        container = None

        execution: dict[str, Any] = {
            "agents": {},
            "models": {},
        }

        agent_result: Any = None
        runtime_error: str | None = None
        runtime_error_type: str | None = None

        before_files: set[str] = set()
        before_contents: dict[str, str] = {}

        after_files: set[str] = set()
        after_contents: dict[str, str] = {}

        changed_files: list[str] = []

        validation: dict[str, Any] = {
            "success": False,
            "missing_files": [],
            "unexpected_files": [],
            "forbidden_files_changed": [],
            "tests": [],
        }

        try:

            # -------------------------------------------------
            # Setup
            # -------------------------------------------------

            self.setup_workspace(
                workspace,
                task,
            )

            # -------------------------------------------------
            # Snapshot BEFORE
            # -------------------------------------------------

            before_files = self.snapshot_files(
                workspace
            )

            before_contents = (
                self.snapshot_file_contents(
                    workspace
                )
            )

            # -------------------------------------------------
            # Run AI-Studio
            # -------------------------------------------------

            container = MainContainer(
                workspace_path=workspace
            )

            try:

                agent_result = (
                    container.orchestrator.run(
                        task["task"]
                    )
                )

            except Exception as error:

                runtime_error = str(error)
                runtime_error_type = type(
                    error
                ).__name__

                # ---------------------------------------------
                # Preserve execution trace even on failure
                # ---------------------------------------------

                orchestrator = getattr(
                    container,
                    "orchestrator",
                    None,
                )

                last_execution = getattr(
                    orchestrator,
                    "last_execution",
                    None,
                )

                execution = self.normalize_execution(
                    last_execution
                )

                execution["runtime_error"] = {
                    "type": runtime_error_type,
                    "message": runtime_error,
                }

                # Do not re-raise here.
                #
                # A benchmark runtime exception is itself a
                # benchmark result and must be persisted.
                agent_result = None

            else:

                # ---------------------------------------------
                # Successful orchestrator return
                # ---------------------------------------------

                orchestrator = getattr(
                    container,
                    "orchestrator",
                    None,
                )

                last_execution = getattr(
                    orchestrator,
                    "last_execution",
                    None,
                )

                execution = self.normalize_execution(
                    last_execution
                )

            # -------------------------------------------------
            # Models
            # -------------------------------------------------

            models = self.collect_models(
                container,
                execution,
            )

            # Keep model information synchronized with the
            # execution trace.
            execution["models"] = {
                **execution.get(
                    "models",
                    {},
                ),
                **models,
            }

            # -------------------------------------------------
            # Snapshot AFTER
            # -------------------------------------------------

            after_files = self.snapshot_files(
                workspace
            )

            after_contents = (
                self.snapshot_file_contents(
                    workspace
                )
            )

            # -------------------------------------------------
            # Detect changes
            # -------------------------------------------------

            changed_files = sorted(
                self.detect_changed_files(
                    before_files,
                    after_files,
                    before_contents,
                    after_contents,
                )
            )

            # -------------------------------------------------
            # Validate
            # -------------------------------------------------

            validation = (
                self.validate_success_criteria(
                    task,
                    workspace,
                    changed_files,
                )
            )

            # -------------------------------------------------
            # Runtime exception always means benchmark FAIL
            # -------------------------------------------------

            if runtime_error is not None:

                validation["success"] = False

                validation["runtime_error"] = {
                    "type": runtime_error_type,
                    "message": runtime_error,
                }

            # -------------------------------------------------
            # Final result
            # -------------------------------------------------

            benchmark_success = (
                validation["success"]
                and runtime_error is None
            )

            benchmark_result = {
                "id": task["id"],
                "name": task["name"],
                "success": benchmark_success,
                "agent_result": agent_result,
                "changed_files": changed_files,
                "validation": validation,
                "models": models,
                "execution": execution,
            }

            self._save_result(
                task_id,
                benchmark_result,
            )

            return benchmark_result

        except Exception as error:

            # =================================================
            # Runner-level failure
            #
            # This is different from an agent failure.
            # We still persist it as a benchmark result.
            # =================================================

            runtime_error = str(error)
            runtime_error_type = type(
                error
            ).__name__

            try:

                after_files = self.snapshot_files(
                    workspace
                )

                after_contents = (
                    self.snapshot_file_contents(
                        workspace
                    )
                )

                changed_files = sorted(
                    self.detect_changed_files(
                        before_files,
                        after_files,
                        before_contents,
                        after_contents,
                    )
                )

            except Exception:
                changed_files = []

            execution = self.normalize_execution(
                execution
            )

            execution["runtime_error"] = {
                "type": runtime_error_type,
                "message": runtime_error,
            }

            models = self.collect_models(
                container,
                execution,
            )

            execution["models"] = {
                **execution.get(
                    "models",
                    {},
                ),
                **models,
            }

            validation = {
                "success": False,
                "missing_files": [],
                "unexpected_files": [],
                "forbidden_files_changed": [],
                "tests": [],
                "runtime_error": {
                    "type": runtime_error_type,
                    "message": runtime_error,
                },
            }

            benchmark_result = {
                "id": task.get(
                    "id",
                    task_id,
                ),
                "name": task.get(
                    "name",
                    task_id,
                ),
                "success": False,
                "agent_result": agent_result,
                "changed_files": changed_files,
                "validation": validation,
                "models": models,
                "execution": execution,
            }

            # ---------------------------------------------
            # IMPORTANT:
            # Even a BenchmarkRunner-level exception is
            # persisted.
            # ---------------------------------------------

            try:

                self._save_result(
                    task_id,
                    benchmark_result,
                )

            except Exception:
                # Never hide the original benchmark error
                # because result persistence itself failed.
                pass

            return benchmark_result

        finally:

            if container is not None:

                watcher = getattr(
                    getattr(
                        container,
                        "development",
                        None,
                    ),
                    "watcher",
                    None,
                )

                if watcher is not None:

                    try:
                        watcher.stop()

                    except Exception:
                        pass

            shutil.rmtree(
                workspace,
                ignore_errors=True,
            )

    # =========================================================
    # Validation
    # =========================================================

    def validate_success_criteria(
        self,
        task: dict[str, Any],
        workspace: Path,
        changed_files: set[str] | list[str],
    ) -> dict[str, Any]:

        criteria = task.get(
            "success_criteria",
            {},
        )

        if not isinstance(
            criteria,
            dict,
        ):
            criteria = {}

        # -----------------------------------------------------
        # Required files
        # -----------------------------------------------------

        required_files = criteria.get(
            "required_files",
            [],
        )

        if not isinstance(
            required_files,
            list,
        ):
            required_files = []

        missing_files = [
            filename
            for filename in required_files
            if not (
                workspace / filename
            ).is_file()
        ]

        # -----------------------------------------------------
        # Allowed changed files
        # -----------------------------------------------------

        allowed_changed_files = criteria.get(
            "allowed_changed_files",
            [],
        )

        if not isinstance(
            allowed_changed_files,
            list,
        ):
            allowed_changed_files = []

        if not allowed_changed_files:
            allowed_changed_files = required_files

        unexpected_files = [
            filename
            for filename in changed_files
            if filename not in allowed_changed_files
        ]

        # -----------------------------------------------------
        # Forbidden files
        # -----------------------------------------------------

        forbidden_files = criteria.get(
            "forbidden_files",
            [],
        )

        if not isinstance(
            forbidden_files,
            list,
        ):
            forbidden_files = []

        forbidden_files_changed = [
            filename
            for filename in changed_files
            if filename in forbidden_files
        ]

        # -----------------------------------------------------
        # Tests
        # -----------------------------------------------------

        tests = criteria.get(
            "tests",
            [],
        )

        if not isinstance(
            tests,
            list,
        ):
            tests = []

        test_results = []

        for test in tests:

            if not isinstance(
                test,
                str,
            ):
                continue

            test_results.append(
                self.run_test(
                    test,
                    workspace,
                    required_files,
                )
            )

        tests_passed = all(
            result["success"]
            for result in test_results
        )

        # -----------------------------------------------------
        # Final result
        # -----------------------------------------------------

        success = (
            not missing_files
            and not unexpected_files
            and not forbidden_files_changed
            and tests_passed
        )

        return {
            "success": success,
            "missing_files": missing_files,
            "unexpected_files": unexpected_files,
            "forbidden_files_changed": (
                forbidden_files_changed
            ),
            "tests": test_results,
        }

    # =========================================================
    # Tests
    # =========================================================

    def run_test(
        self,
        test: str,
        workspace: Path,
        required_files: list[str],
    ) -> dict[str, Any]:

        namespace: dict[str, Any] = {}

        try:

            for filename in required_files:

                path = (
                    workspace
                    / filename
                )

                if not path.is_file():

                    return {
                        "test": test,
                        "success": False,
                        "error": (
                            "Required file not found: "
                            f"{filename}"
                        ),
                    }

                source = path.read_text(
                    encoding="utf-8"
                )

                exec(
                    compile(
                        source,
                        str(path),
                        "exec",
                    ),
                    namespace,
                )

            exec(
                test,
                namespace,
            )

            return {
                "test": test,
                "success": True,
            }

        except Exception as error:

            return {
                "test": test,
                "success": False,
                "error": str(error),
                "error_type": type(
                    error
                ).__name__,
            }

    # =========================================================
    # Result persistence
    # =========================================================

    def _save_result(
        self,
        task_id: str,
        result: dict[str, Any],
    ) -> None:

        result_path = (
            self.results_dir
            / f"{task_id}.json"
        )

        # -----------------------------------------------------
        # Load previous history
        # -----------------------------------------------------

        if result_path.exists():

            try:

                with result_path.open(
                    "r",
                    encoding="utf-8",
                ) as file:

                    history = json.load(
                        file
                    )

            except (
                json.JSONDecodeError,
                OSError,
            ):

                history = {}

        else:

            history = {}

        if not isinstance(
            history,
            dict,
        ):
            history = {}

        # -----------------------------------------------------
        # Existing runs
        # -----------------------------------------------------

        runs = history.get(
            "runs",
            [],
        )

        if not isinstance(
            runs,
            list,
        ):
            runs = []

        run_id = len(runs) + 1

        # -----------------------------------------------------
        # New run
        # -----------------------------------------------------

        run = {
            "run_id": run_id,
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "success": result.get(
                "success",
                False,
            ),
            "agent_result": result.get(
                "agent_result",
            ),
            "changed_files": result.get(
                "changed_files",
                [],
            ),
            "validation": result.get(
                "validation",
                {},
            ),
            "models": result.get(
                "models",
                {},
            ),
            "execution": result.get(
                "execution",
                {},
            ),
        }

        runs.append(
            run
        )

        # -----------------------------------------------------
        # Statistics
        # -----------------------------------------------------

        passed_runs = sum(
            1
            for item in runs
            if (
                isinstance(item, dict)
                and item.get("success") is True
            )
        )

        failed_runs = sum(
            1
            for item in runs
            if (
                isinstance(item, dict)
                and item.get("success") is False
            )
        )

        total_runs = (
            passed_runs
            + failed_runs
        )

        pass_rate = (
            (passed_runs / total_runs) * 100
            if total_runs
            else 0.0
        )

        fail_rate = (
            (failed_runs / total_runs) * 100
            if total_runs
            else 0.0
        )

        # -----------------------------------------------------
        # History document
        # -----------------------------------------------------

        history = {
            "meta": {
                "id": result.get(
                    "id",
                    task_id,
                ),
                "name": result.get(
                    "name",
                    task_id,
                ),
                "total_runs": total_runs,
                "passed_runs": passed_runs,
                "failed_runs": failed_runs,
                "pass_rate": round(
                    pass_rate,
                    2,
                ),
                "fail_rate": round(
                    fail_rate,
                    2,
                ),
            },
            "runs": runs,
        }

        # -----------------------------------------------------
        # Save
        # -----------------------------------------------------

        with result_path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                history,
                file,
                indent=2,
                ensure_ascii=False,
            )