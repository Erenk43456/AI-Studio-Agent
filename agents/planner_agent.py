from agents.base_agent import BaseAgent

from app.core.logger import AppLogger
from agents.planner.llm_planner import create_llm_plan


class PlannerAgent(BaseAgent):

    def __init__(
        self,
        llm,
        memory=None,
        registry=None
    ):

        super().__init__(
            "Planner Agent",
            memory
        )

        self.llm = llm
        self.registry = registry

        self.logger = AppLogger()

    # =============================================================
    # Public API
    # =============================================================

    def create_plan(
        self,
        task
    ):

        if task is None:
            original_task = ""

        else:
            original_task = str(task).strip()

        self.logger.info(
            f"Creating plan for: {original_task}"
        )

        if not original_task:

            return {
                "steps": [
                    {
                        "tool": "code",
                        "action": "implement",
                        "input": ""
                    }
                ]
            }

        # =========================================================
        # Save last task
        # =========================================================

        if self.memory:

            try:

                self.memory.save(
                    "last_task",
                    original_task,
                    "system"
                )

            except Exception as error:

                self.logger.error(
                    f"Failed to save last task: {error}"
                )

        # =========================================================
        # Tool descriptions
        # =========================================================

        tool_descriptions = None

        if self.registry:

            try:

                tool_descriptions = (
                    self.registry.get_tool_descriptions()
                )

            except Exception as error:

                self.logger.error(
                    f"Failed to load tool descriptions: {error}"
                )

        # =========================================================
        # LLM Planner
        # =========================================================

        try:

            plan = create_llm_plan(
                self.llm,
                original_task,
                tool_descriptions
            )

            # -----------------------------------------------------
            # Valid plan
            # -----------------------------------------------------

            if isinstance(plan, dict):

                plan = self._validate_plan(
                    plan,
                    original_task
                )

                plan["user_message"] = original_task

                return plan

            # -----------------------------------------------------
            # Invalid / unavailable planner result
            # -----------------------------------------------------

            self.logger.warning(
                "LLM planner returned no valid plan. "
                "Using deterministic fallback."
            )

            return self._fallback_plan(
                original_task
            )

        except Exception as error:

            self.logger.error(
                f"Planner error: {error}"
            )

            return self._fallback_plan(
                original_task
            )

    # =============================================================
    # Plan validation
    # =============================================================

    def _validate_plan(
        self,
        plan,
        task
    ):

        if not isinstance(
            plan,
            dict
        ):

            return self._fallback_plan(
                task
            )

        steps = plan.get(
            "steps"
        )

        if not isinstance(
            steps,
            list
        ):

            return self._fallback_plan(
                task
            )

        valid_steps = []

        for step in steps:

            if not isinstance(
                step,
                dict
            ):

                continue

            tool = step.get(
                "tool"
            )

            action = step.get(
                "action"
            )

            if not tool or not action:

                continue

            # -----------------------------------------------------
            # Never allow the LLM to invent tools.
            # -----------------------------------------------------

            if not self._tool_exists(
                tool
            ):

                self.logger.warning(
                    f"Planner selected unavailable tool: {tool}"
                )

                continue

            valid_steps.append(
                step
            )

        if not valid_steps:

            return self._fallback_plan(
                task
            )

        return {
            "steps": valid_steps
        }

    # =============================================================
    # Tool existence
    # =============================================================

    def _tool_exists(
        self,
        tool_name
    ):

        if not self.registry:

            # No registry means we cannot validate.
            return True

        try:

            tool = self.registry.get(
                tool_name
            )

            return tool is not None

        except Exception as error:

            self.logger.error(
                f"Tool lookup failed for '{tool_name}': {error}"
            )

            return False

    # =============================================================
    # Deterministic fallback
    # =============================================================

    def _fallback_plan(
        self,
        task
    ):

        text = str(
            task or ""
        ).strip()

        lower = text.lower()

        # ---------------------------------------------------------
        # Development / coding request
        # ---------------------------------------------------------

        development_indicators = (
            "düzelt",
            "hata",
            "hataları",
            "bug",
            "error",
            "fix",
            "implement",
            "implementation",
            "ekle",
            "oluştur",
            "geliştir",
            "iyileştir",
            "refactor",
            "refactoring",
            "kod",
            "dosya",
            ".py",
            ".rs",
            ".js",
            ".ts",
            ".cpp",
            ".h"
        )

        is_development = any(
            indicator in lower
            for indicator in development_indicators
        )

        if is_development:

            self.logger.warning(
                "Using deterministic CODE fallback."
            )

            return {
                "steps": [
                    {
                        "tool": "code",
                        "action": "implement",
                        "input": text
                    }
                ],
                "user_message": text
            }

        # ---------------------------------------------------------
        # Project analysis
        # ---------------------------------------------------------

        analysis_indicators = (
            "analiz et",
            "analiz",
            "incele",
            "analyze",
            "inspect",
            "architecture",
            "mimari"
        )

        if any(
            indicator in lower
            for indicator in analysis_indicators
        ):

            if self._tool_exists(
                "repository_analyzer"
            ):

                return {
                    "steps": [
                        {
                            "tool": "repository_analyzer",
                            "action": "analyze",
                            "input": text
                        }
                    ],
                    "user_message": text
                }

        # ---------------------------------------------------------
        # Last-resort development fallback
        # ---------------------------------------------------------

        self.logger.warning(
            "No specialized fallback matched. "
            "Using deterministic CODE fallback."
        )

        return {
            "steps": [
                {
                    "tool": "code",
                    "action": "implement",
                    "input": text
                }
            ],
            "user_message": text
        }