from agents.base_agent import BaseAgent

from app.core.logger import AppLogger

import json
import re


class CodeAgent(BaseAgent):

    def __init__(
        self,
        llm,
        registry,
        memory=None,
        workspace=None
    ):

        super().__init__(
            "Code Agent",
            memory
        )

        self.llm = llm
        self.registry = registry
        self.workspace = workspace
        self.logger = AppLogger()

    def execute(
        self,
        plan
    ):

        if isinstance(plan, dict):

            task = (
                plan.get("input")
                or
                plan.get("message")
                or
                plan.get("task")
                or
                ""
            )

        else:

            task = str(plan)

        return self.run(task)

    def run(
        self,
        task
    ):

        self.logger.info(
            f"Code task: {task}"
        )

        repository = self._analyze_repository()

        prompt = f"""
You are a senior autonomous software engineer.

You are modifying an existing Python AI agent framework.

Project:

AI-Studio-Agent

Repository analysis:

{repository}

User request:

{task}

Your responsibilities:

1. Understand the existing architecture.
2. Identify exactly which files must change.
3. Explain why those files are affected.
4. Design the implementation.
5. Produce a structured modification plan.

Rules:

- Respect existing architecture.
- Do not invent files.
- Do not rewrite unrelated code.
- Prefer minimal changes.
- Consider dependency injection.
- Consider existing agents, tools and memory systems.
- Think like a production software engineer.

Return JSON only.

Format:

{{
    "summary": "",

    "files": [

        {{
            "path": "",
            "purpose": "",
            "changes": [
                ""
            ]
        }}

    ],

    "implementation": [

        ""

    ],

    "risks": [

        ""

    ]
}}
"""

        response = self.llm.generate(
            prompt,
            max_tokens=6000
        )

        if isinstance(response, dict):

            self.logger.error(
                f"Code Agent LLM error {response}"
            )

            return {
                "error": "Code Agent LLM request failed.",
                "details": response
            }

        if not isinstance(response, str):

            self.logger.error(
                f"Unexpected LLM response type: {type(response)}"
            )

            return {
                "error": "Unexpected LLM response type"
            }

        # ---------------------------------------------------------
        # Parse implementation plan
        # ---------------------------------------------------------

        implementation_plan = self._parse_implementation_plan(
            response
        )

        # ---------------------------------------------------------
        # Automatic JSON recovery
        # ---------------------------------------------------------

        if implementation_plan is None:

            self.logger.warning(
                "Initial implementation plan JSON was invalid. "
                "Requesting JSON repair from LLM."
            )

            repaired_response = self._repair_json(
                response
            )

            if repaired_response is not None:

                implementation_plan = (
                    self._parse_implementation_plan(
                        repaired_response
                    )
                )

        # ---------------------------------------------------------
        # Failed JSON recovery
        # ---------------------------------------------------------

        if implementation_plan is None:

            self.logger.error(
                "Unable to obtain valid implementation plan JSON."
            )

            return {
                "error": "LLM returned invalid JSON.",
                "raw": response
            }

        # ---------------------------------------------------------
        # Code writer
        # ---------------------------------------------------------

        writer = self.registry.get(
            "code_writer"
        )

        if writer is None:

            return implementation_plan

        write_result = writer.execute(
            implementation_plan
        )

        success = False

        if isinstance(write_result, dict):

            success = write_result.get(
                "success",
                False
            )

        return {
            "success": success,
            "plan": implementation_plan,
            "write_result": write_result
        }

    def _analyze_repository(
        self
    ):

        tool = self.registry.get(
            "repository_analyzer"
        )

        if tool is None:

            return (
                "Repository analyzer unavailable."
            )

        try:

            result = tool.execute({
                "action": "analyze"
            })

            return str(result)

        except Exception as error:

            self.logger.error(
                f"Repository analysis error: {error}"
            )

            return (
                "Repository analysis failed."
            )

    def _parse_implementation_plan(
        self,
        response
    ):
        """
        Extract and parse an implementation plan
        from an LLM response.
        """

        if not isinstance(response, str):

            return None

        cleaned = self.clean_json(
            response
        )

        try:

            result = json.loads(
                cleaned
            )

            if isinstance(result, dict):

                return result

        except (
            json.JSONDecodeError,
            TypeError
        ) as error:

            self.logger.warning(
                f"Implementation plan JSON parse failed: {error}"
            )

        return None

    def _repair_json(
        self,
        response
    ):
        """
        Ask the LLM to repair malformed JSON.
        """

        repair_prompt = f"""
You are a JSON repair engine.

The following response was supposed to be a valid JSON
implementation plan but contains invalid JSON syntax.

Repair ONLY the JSON syntax.

Do not change the meaning.
Do not add explanations.
Do not use markdown.
Do not use code fences.

Return valid JSON only.

Invalid response:

{response}

Return the corrected JSON.
"""

        try:

            repaired = self.llm.generate(
                repair_prompt,
                max_tokens=2500
            )

            if isinstance(repaired, dict):

                self.logger.error(
                    f"JSON repair LLM error: {repaired}"
                )

                return None

            if not isinstance(repaired, str):

                self.logger.error(
                    f"Unexpected JSON repair response type: "
                    f"{type(repaired)}"
                )

                return None

            return repaired

        except Exception as error:

            self.logger.error(
                f"JSON repair failed: {error}"
            )

            return None

    def clean_json(
        self,
        text
    ):

        if not text:

            return "{}"

        if not isinstance(text, str):

            return "{}"

        text = text.replace(
            "```json",
            ""
        )

        text = text.replace(
            "```",
            ""
        )

        match = re.search(
            r"\{[\s\S]*\}",
            text
        )

        if match:

            return match.group()

        return text