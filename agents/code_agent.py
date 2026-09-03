import json
import re

from agents.base_agent import BaseAgent
from app.core.logger import AppLogger


class CodeAgent(BaseAgent):

    def __init__(
        self,
        llm,
        registry,
        memory=None,
        workspace=None,
        development_context=None
    ):

        super().__init__(
            "Code Agent",
            memory
        )

        self.llm = llm
        self.registry = registry
        self.workspace = workspace
        self.development_context = development_context

        self.logger = AppLogger()

    # =============================================================
    # Execute
    # =============================================================

    def execute(
        self,
        plan
    ):

        if isinstance(plan, dict):

            task = (
                plan.get("input")
                or plan.get("message")
                or plan.get("task")
                or ""
            )

        else:

            task = str(plan)

        return self.run(task)

    # =============================================================
    # Run
    # =============================================================

    def run(
        self,
        task,
        development_context=None
    ):

        self.logger.info(
            f"Code task: {task}"
        )

        context = (
            development_context
            or self._build_context(task)
        )

        repository = self._get_repository_context(
            context
        )

        context_text = self._format_context(
            context,
            repository
        )

        prompt = f"""
You are the senior software engineering agent
inside the AI-Studio-Agent framework.

You are modifying an EXISTING project.

You must work WITH the existing architecture.

==================================================
USER REQUEST
==================================================

{task}

==================================================
DEVELOPMENT CONTEXT
==================================================

{context_text}

==================================================
ENGINEERING OBJECTIVE
==================================================

Use the DevelopmentContext as the primary source
of architectural truth.

The .ai_memory information describes the current
project architecture and known file relationships.

Do NOT assume a generic Python architecture.

==================================================
DEVELOPMENT ALGORITHM
==================================================

Follow the strategy provided by DevelopmentContext.

General rules:

1. Identify the target files.
2. Inspect their project-memory information.
3. Inspect related files from project memory.
4. Understand dependency relationships.
5. Identify the smallest architectural change.
6. Preserve existing architecture.
7. Preserve public APIs.
8. Preserve dependency injection.
9. Preserve existing classes.
10. Preserve existing public methods.
11. Do not invent managers, registries, providers,
    agents or architectures.
12. Do not modify unrelated files.
13. Do not rewrite a complete file unless necessary.
14. Prefer minimal changes.
15. Validate the resulting implementation.

==================================================
EXISTING SYSTEMS
==================================================

The project already has:

- ProjectMemory
- RepositoryAnalyzer
- CodeAnalyzer
- CodeRepair
- CodeWriter
- WorkspaceWatcher / AIWatch
- dependency injection containers
- development orchestration
- DevelopmentContext

Do NOT create replacements for these systems.

Integrate with the existing architecture.

==================================================
IMPLEMENTATION PLAN REQUIREMENTS
==================================================

Return ONLY one valid JSON object.

The JSON MUST use exactly this structure:

{{
    "summary": "short description",
    "files": [
        {{
            "path": "relative/path.py",
            "purpose": "why this file must change",
            "changes": [
                "specific change 1",
                "specific change 2"
            ]
        }}
    ],
    "implementation": [
        "implementation instruction 1",
        "implementation instruction 2"
    ],
    "risks": [
        "risk 1"
    ]
}}

CRITICAL JSON RULES:

- Use double quotes for JSON strings.
- Escape internal double quotes.
- Do not use single quotes as JSON delimiters.
- Do not include trailing commas.
- Do not include Markdown.
- Do not use code fences.
- Do not include comments.
- Do not include text before the JSON.
- Do not include text after the JSON.
- Return syntactically valid JSON only.

IMPORTANT:

The response will be parsed directly by Python json.loads().
A response that is not valid JSON will be rejected.
"""

        try:

            response = self.llm.generate(
                prompt,
                max_tokens=6000
            )

        except Exception as error:

            self.logger.error(
                f"Code planning failed: {error}"
            )

            return {
                "success": False,
                "error": str(error)
            }

        if isinstance(response, dict):

            self.logger.error(
                f"Code Agent LLM error: {response}"
            )

            return {
                "success": False,
                "error": "Code Agent LLM request failed.",
                "details": response
            }

        if not isinstance(response, str):

            self.logger.error(
                f"Unexpected LLM response type: {type(response)}"
            )

            return {
                "success": False,
                "error": "Unexpected LLM response type."
            }

        implementation_plan = (
            self._parse_implementation_plan(
                response
            )
        )

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

        if implementation_plan is None:

            self.logger.error(
                "Unable to obtain valid implementation plan JSON."
            )

            return {
                "success": False,
                "error": "LLM returned invalid JSON.",
                "raw": response
            }

        implementation_plan = (
            self._normalize_plan(
                implementation_plan
            )
        )

        writer = self.registry.get(
            "code_writer"
        )

        if writer is None:

            self.logger.error(
                "Code writer unavailable."
            )

            return {
                "success": False,
                "plan": implementation_plan,
                "error": "Code writer unavailable."
            }

        implementation_plan[
            "development_context"
        ] = context

        try:

            write_result = writer.execute(
                implementation_plan
            )

        except Exception as error:

            self.logger.error(
                f"Code writer failed: {error}"
            )

            return {
                "success": False,
                "plan": implementation_plan,
                "error": str(error)
            }

        success = (
            isinstance(
                write_result,
                dict
            )
            and write_result.get(
                "success",
                False
            )
        )

        return {
            "success": success,
            "plan": implementation_plan,
            "write_result": write_result
        }

    # =============================================================
    # Development context
    # =============================================================

    def _build_context(
        self,
        task
    ):

        if self.development_context is None:

            return {
                "task": task,
                "strategy": {
                    "type": "legacy_development",
                    "repository_analysis_fallback": True
                }
            }

        try:

            context = self.development_context.build(
                task
            )

            if isinstance(
                context,
                dict
            ):

                return context

        except Exception as error:

            self.logger.error(
                f"Development context failed: {error}"
            )

        return {
            "task": task,
            "strategy": {
                "type": "legacy_development",
                "repository_analysis_fallback": True
            }
        }

    # =============================================================
    # Repository fallback
    # =============================================================

    def _get_repository_context(
        self,
        context
    ):

        if not isinstance(
            context,
            dict
        ):

            return ""

        strategy = context.get(
            "strategy",
            {}
        )

        if not isinstance(
            strategy,
            dict
        ):

            return ""

        if not strategy.get(
            "repository_analysis_fallback",
            True
        ):

            return ""

        architecture = context.get(
            "architecture"
        )

        if isinstance(
            architecture,
            dict
        ):

            if architecture.get(
                "repository_analysis"
            ):

                return (
                    "RepositoryAnalyzer data is already "
                    "available in ProjectMemory."
                )

        else:

            architecture = {}

        analysis = self._analyze_repository()

        if not analysis:

            return ""

        if isinstance(
            analysis,
            dict
        ):

            architecture[
                "repository_analysis"
            ] = analysis

            context[
                "architecture"
            ] = architecture

            return str(
                analysis
            )

        return str (
            analysis
        )

    # =============================================================
    # Repository analyzer
    # =============================================================

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

            return  result

        except Exception as error:

            self.logger.error(
                f"Repository analysis error: {error}"
            )

            return (
                "Repository analysis failed."
            )

    # =============================================================
    # Context formatting
    # =============================================================

    def _format_context(
        self,
        context,
        repository
    ):

        try:

            serialized = json.dumps(
                context,
                indent=2,
                ensure_ascii=False,
                default=str
            )

        except Exception:

            serialized = str(
                context
            )

        if repository:

            serialized += (
                "\n\n"
                "==================================================\n"
                "REPOSITORY FALLBACK\n"
                "==================================================\n\n"
                f"{repository}"
            )

        return serialized

    # =============================================================
    # Implementation plan parser
    # =============================================================

    def _parse_implementation_plan(
        self,
        response
    ):

        if not isinstance(
            response,
            str
        ):

            return None

        cleaned = self.clean_json(
            response
        )

        try:

            result = json.loads(
                cleaned
            )

            if isinstance(
                result,
                dict
            ):

                return result

        except (
            json.JSONDecodeError,
            TypeError,
            ValueError
        ) as error:

            self.logger.warning(
                f"Implementation plan JSON parse failed: {error}"
            )

        extracted = self._extract_json_object(
            response
        )

        if extracted is None:

            return None

        try:

            result = json.loads(
                extracted
            )

            if isinstance(
                result,
                dict
            ):

                return result

        except (
            json.JSONDecodeError,
            TypeError,
            ValueError
        ) as error:

            self.logger.warning(
                f"Extracted JSON parse failed: {error}"
            )

        return None

    # =============================================================
    # JSON repair
    # =============================================================

    def _repair_json(
        self,
        response
    ):

        repair_prompt = f"""
You are a strict JSON repair engine.

The following response was supposed to be a valid JSON
implementation plan.

Repair ONLY the JSON syntax.

Do not change the meaning.

Do not add explanations.

Do not use Markdown.

Do not use code fences.

Do not add comments.

Return ONE valid JSON object only.

Required structure:

{{
    "summary": "",
    "files": [
        {{
            "path": "",
            "purpose": "",
            "changes": []
        }}
    ],
    "implementation": [],
    "risks": []
}}

Rules:

- Use double quotes.
- Escape internal double quotes.
- Remove trailing commas.
- Preserve all information.
- Return valid JSON only.

BROKEN RESPONSE:

{response}
"""

        try:

            repaired = self.llm.generate(
                repair_prompt,
                max_tokens=4000
            )

        except Exception as error:

            self.logger.error(
                f"JSON repair failed: {error}"
            )

            return None

        if isinstance(
            repaired,
            dict
        ):

            self.logger.error(
                f"JSON repair LLM error: {repaired}"
            )

            return None

        if not isinstance(
            repaired,
            str
        ):

            self.logger.error(
                "JSON repair returned an invalid response type."
            )

            return None

        return repaired

    # =============================================================
    # Plan normalization
    # =============================================================

    def _normalize_plan(
        self,
        plan
    ):

        if not isinstance(
            plan,
            dict
        ):

            return {
                "summary": "",
                "files": [],
                "implementation": [],
                "risks": []
            }

        files = plan.get(
            "files",
            []
        )

        implementation = plan.get(
            "implementation",
            []
        )

        risks = plan.get(
            "risks",
            []
        )

        if not isinstance(
            files,
            list
        ):

            files = []

        if not isinstance(
            implementation,
            list
        ):

            implementation = []

        if not isinstance(
            risks,
            list
        ):

            risks = []

        normalized = {
            "summary": str(
                plan.get(
                    "summary",
                    ""
                )
            ),

            "files": [],

            "implementation": [
                str(item)
                for item in implementation
            ],

            "risks": [
                str(item)
                for item in risks
            ]
        }

        for file in files:

            if not isinstance(
                file,
                dict
            ):

                continue

            path = file.get(
                "path"
            )

            if not path:

                continue

            changes = file.get(
                "changes",
                []
            )

            if not isinstance(
                changes,
                list
            ):

                changes = [
                    str(changes)
                ]

            normalized["files"].append(
                {
                    "path": str(
                        path
                    ),

                    "purpose": str(
                        file.get(
                            "purpose",
                            ""
                        )
                    ),

                    "changes": [
                        str(change)
                        for change in changes
                    ]
                }
            )

        return normalized

    # =============================================================
    # Balanced JSON extraction
    # =============================================================

    def _extract_json_object(
        self,
        text
    ):

        if not isinstance(
            text,
            str
        ):

            return None

        start = text.find(
            "{"
        )

        if start == -1:

            return None

        depth = 0
        in_string = False
        escaped = False

        for index in range(
            start,
            len(text)
        ):

            char = text[index]

            if in_string:

                if escaped:

                    escaped = False

                elif char == "\\":
                    escaped = True

                elif char == '"':
                    in_string = False

                continue

            if char == '"':

                in_string = True

                continue

            if char == "{":

                depth += 1

            elif char == "}":

                depth -= 1

                if depth == 0:

                    return text[
                        start:index + 1
                    ]

        return None

    # =============================================================
    # JSON cleanup
    # =============================================================

    def clean_json(
        self,
        text
    ):

        if not text:

            return "{}"

        if not isinstance(
            text,
            str
        ):

            return "{}"

        text = text.strip()

        text = re.sub(
            r"```(?:json)?",
            "",
            text,
            flags=re.IGNORECASE
        )

        text = re.sub(
            r"```",
            "",
            text
        )

        text = text.strip()

        extracted = self._extract_json_object(
            text
        )

        if extracted:

            return extracted

        return text