import re

from typing import Any, List, Union

from agents.base_agent import BaseAgent
from agents.contract_agent import ContractAgent
from agents.contracts.planner import PlannerContract, PlannerStep
from agents.contracts.tool import ToolStepContract
from agents.contracts.result import ToolResultContract
from app.core.logger import AppLogger


class ToolAgent(BaseAgent):

    def __init__(
        self,
        registry,
        memory=None,
        llm=None,
        code_agent=None,
        contract_agent=None,
    ):
        super().__init__("Tool Agent", memory)

        self.registry = registry
        self.llm = llm
        self.code_agent = code_agent
        self.contract_agent = contract_agent or ContractAgent()
        self.logger = AppLogger()

    def execute_steps(
        self,
        plan: Union[PlannerContract, dict, Any],
        development_context=None,
    ) -> List[dict]:

        if not plan:
            return [
                {
                    "tool": None,
                    "action": None,
                    "result": self.contract_agent.to_tool_result_contract(
                        {
                            "success": False,
                            "error": "Invalid plan.",
                        }
                    ),
                }
            ]

        plan_contract = self.contract_agent.to_planner_contract(plan)
        steps = plan_contract.steps

        if not steps:
            return self.execute(plan)

        results = []
        context = ""

        for index, step in enumerate(steps):
            step_contract: ToolStepContract = (
                self.contract_agent.to_tool_step_contract(step)
            )

            tool_name = step_contract.tool
            action = step_contract.action

            if not tool_name or not action:
                result = self.contract_agent.to_tool_result_contract(
                    {
                        "success": False,
                        "error": "Invalid planner step.",
                    }
                )

                results.append(
                    {
                        "step": index + 1,
                        "tool": None,
                        "action": None,
                        "filename": None,
                        "input": None,
                        "result": result,
                    }
                )

                context = str(result)
                continue

            self.logger.info(
                f"Executing step {index + 1}/{len(steps)}: {tool_name}"
            )

            # Context propagation
            if context:
                step_contract.context["previous_context"] = context

                if action == "write":
                    content = step_contract.parameters.get("content")

                    if not content:
                        if self.should_generate_code(step_contract):
                            step_contract.parameters["content"] = (
                                self.generate_code_change(
                                    step_contract,
                                    context,
                                )
                            )
                        else:
                            step_contract.parameters["content"] = (
                                self.prepare_write_content(
                                    step_contract.input,
                                    context,
                                )
                            )

            # Tool execution
            if tool_name == "code" and self.code_agent:
                try:
                    raw_result = self.code_agent.run(
                        step_contract.input,
                        development_context,
                    )

                    result = (
                        self.contract_agent.to_tool_result_contract(
                            raw_result
                        )
                    )

                except Exception as error:
                    self.logger.error(
                        f"Code execution error: {error}"
                    )

                    result = (
                        self.contract_agent.to_tool_result_contract(
                            {
                                "success": False,
                                "tool": "code",
                                "error": str(error),
                            }
                        )
                    )

            else:
                raw_result = self.execute(step_contract)

                result = (
                    self.contract_agent.to_tool_result_contract(
                        raw_result
                    )
                )

            if isinstance(result, str):
                context = result
            elif hasattr(result, "message") and result.message:
                context = str(result.message)
            else:
                context = str(result)

            results.append(
                {
                    "step": index + 1,
                    "tool": tool_name,
                    "action": action,
                    "filename": step_contract.parameters.get(
                        "filename"
                    ),
                    "input": step_contract.input,
                    "result": result,
                }
            )

        return results

    def normalize_tool_input(self, plan: Any) -> Any:

        if isinstance(plan, dict):
            plan = plan.copy()
            
        tool_name = (
            getattr(plan, "tool", None)
            or (plan.get("tool") if hasattr(plan, "get") else None)
        )

        if not tool_name:
            return plan

        # FILE TOOL
        if tool_name == "file":
            action = (
                getattr(plan, "action", None)
                or (plan.get("action") if hasattr(plan, "get") else None)
            )

            if action in ("write", "create"):
                content = (
                    plan.get("content")
                    if hasattr(plan, "get")
                    else getattr(plan, "content", None)
                )

                inp = (
                    plan.get("input")
                    if hasattr(plan, "get")
                    else getattr(plan, "input", None)
                )

                if not content and inp:
                    plan["content"] = inp

        # CALCULATOR
        if tool_name != "calculator":
            return plan

        has_numbers = (
            plan.get("numbers")
            if hasattr(plan, "get")
            else getattr(plan, "numbers", None)
        )

        has_operation = (
            plan.get("operation")
            if hasattr(plan, "get")
            else getattr(plan, "operation", None)
        )

        if has_numbers and has_operation:
            return plan

        text = (
            plan.get("input", "")
            if hasattr(plan, "get")
            else getattr(plan, "input", "")
        )

        if not text:
            text = (
                plan.get("user_message", "")
                if hasattr(plan, "get")
                else getattr(plan, "user_message", "")
            )

        numbers = re.findall(
            r"-?\d+(?:\.\d+)?",
            str(text),
        )

        paired_numbers = re.search(
            r"(-?\d+(?:\.\d+)?)\s+ile\s+(-?\d+(?:\.\d+)?)",
            str(text),
            flags=re.IGNORECASE,
        )

        if paired_numbers:
            numbers = [
                paired_numbers.group(1),
                paired_numbers.group(2),
            ]

        if len(numbers) < 2:
            return plan

        operation = None
        lower = str(text).lower()

        if any(
            word in lower
            for word in [
                "+",
                "topla",
                "toplam",
                "artı",
                "kaç eder",
            ]
        ):
            operation = "add"

        elif any(
            word in lower
            for word in [
                "-",
                "çıkar",
                "eksi",
            ]
        ):
            operation = "subtract"

        elif any(
            word in lower
            for word in [
                "*",
                "çarp",
                "çarpı",
            ]
        ):
            operation = "multiply"

        elif any(
            word in lower
            for word in [
                "/",
                "böl",
                "bölü",
            ]
        ):
            operation = "divide"

        if operation:
            plan["operation"] = operation
            plan["numbers"] = numbers

        return plan

    def should_generate_code(self, step: Any) -> bool:
        inp = (
            step.get("input", "")
            if hasattr(step, "get")
            else getattr(step, "input", "")
        )

        text = str(inp).lower()

        keywords = [
            "ekle",
            "oluştur",
            "geliştir",
            "refactor",
            "değiştir",
            "entegre",
            "mimari",
            "sistem",
            "özellik",
            "fonksiyon",
            "class",
            "agent",
        ]

        return any(
            word in text
            for word in keywords
        )

    def generate_code_change(
        self,
        step: Any,
        existing_content: str,
    ) -> str:

        if not self.llm:
            self.logger.error(
                "Code generation failed: LLM is not configured."
            )

            raise RuntimeError(
                "Code generation failed: LLM is not configured."
            )

        inp = (
            step.get("input", "")
            if hasattr(step, "get")
            else getattr(step, "input", "")
        )

        prompt = f"""
You are a senior Python software engineer.

Modify the existing file according to the user request.

Existing file:

{existing_content}

Requested change:

{inp}

Rules:

- Return ONLY complete file content.
- Do not explain.
- Do not use markdown.
- Preserve existing architecture.
- Do not remove existing features.
- Apply only required changes.
- Keep imports correct.

New file:
"""

        try:
            result = self.llm.generate(prompt)
            return result

        except Exception as error:
            self.logger.error(
                f"Code generation error: {error}"
            )

            raise RuntimeError(
                f"Code generation failed: {error}"
            ) from error

    def prepare_write_content(
        self,
        instruction: str,
        existing_content: str,
    ) -> str:

        if not existing_content:
            return ""

        lower_instruction = instruction.lower()

        if any(
            word in lower_instruction
            for word in [
                "en üstüne",
                "başına",
                "top",
            ]
        ):
            if "#" in instruction:
                comment = instruction.split(
                    "#",
                    1,
                )[1]

                comment = re.sub(
                    r"\b(ekle|yaz|koy|getir|başına|en üstüne)\b",
                    "",
                    comment,
                    flags=re.IGNORECASE,
                )

                comment = comment.strip()

                return (
                    "# "
                    + comment
                    + "\n\n"
                    + existing_content
                )

        return existing_content

    def execute(
        self,
        plan: Any,
    ) -> ToolResultContract:

        if not plan:
            return ToolResultContract(
                success=False,
                error="Invalid plan.",
            )

        plan = self.normalize_tool_input(plan)

        tool_name = (
            getattr(plan, "tool", None)
            or (
                plan.get("tool")
                if hasattr(plan, "get")
                else None
            )
        )

        self.logger.info(
            f"Executing tool: {tool_name}"
        )

        if not tool_name:
            return ToolResultContract(
                success=False,
                error="Tool name missing.",
            )

        tool = self.registry.get(
            tool_name
        )

        if (
            tool is None
            and tool_name in [
                "memory_save",
                "memory_get",
            ]
        ):
            tool = self.registry.get(
                "memory"
            )

        if tool is None:
            self.logger.warning(
                f"Tool not found: {tool_name}"
            )

            return ToolResultContract(
                success=False,
                error=f"Tool not found: {tool_name}",
            )

        try:
            if hasattr(tool, "execute"):
                return tool.execute(plan)

            return ToolResultContract(
                success=False,
                error=(
                    f"Tool {tool_name} "
                    "does not support execute method."
                ),
            )

        except Exception as error:
            self.logger.error(
                f"Tool execution error: {error}"
            )

            return ToolResultContract(
                success=False,
                error=f"Tool error: {error}",
            )