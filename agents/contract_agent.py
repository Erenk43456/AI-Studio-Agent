from typing import Any, Union, List, Dict
from agents.contracts.decision import DecisionContract
from agents.contracts.planner import PlannerStep, PlannerContract
from agents.contracts.tool import ToolStepContract
from agents.contracts.result import ToolResultContract
from agents.contracts.memory import MemoryContract


class ContractAgent:
    """
    Central contract agent responsible for validating, normalizing,
    and constructing canonical Contract objects across agent boundaries.

    Architectural guarantees:
    - Does NOT call LLM.
    - Does NOT execute tools.
    - Is NOT an orchestrator.
    - Purely deterministic validation and typed construction.
    """

    ALLOWED_SYSTEMS = {"chat", "memory", "development"}

    # =============================================================
    # Decision Contract
    # =============================================================

    def to_decision_contract(
        self,
        data: Union[dict, DecisionContract, Any],
        default_system: str = "chat",
        default_reason: str = "",
    ) -> DecisionContract:
        """
        Validate and normalize input data into a typed DecisionContract.
        """
        if isinstance(data, DecisionContract):
            system = data.system if data.system in self.ALLOWED_SYSTEMS else default_system
            return DecisionContract(
                system=system,
                action=data.action,
                reason=data.reason or default_reason,
                metadata=dict(data.metadata) if data.metadata else {},
            )

        if isinstance(data, dict):
            raw_system = str(data.get("system", "")).strip().lower()
            system = raw_system if raw_system in self.ALLOWED_SYSTEMS else default_system

            action = str(data.get("action", "")).strip()
            reason = str(data.get("reason", default_reason)).strip()

            # Metadata extraction for any extra fields
            known_keys = {"system", "action", "reason", "metadata"}
            metadata = dict(data.get("metadata", {})) if isinstance(data.get("metadata"), dict) else {}
            for key, val in data.items():
                if key not in known_keys:
                    metadata[key] = val

            return DecisionContract(
                system=system,
                action=action,
                reason=reason,
                metadata=metadata,
            )

        # Fallback for unexpected types
        return DecisionContract(
            system=default_system,
            reason=default_reason or "Fallback decision due to non-dict input",
        )

    # =============================================================
    # Planner Contract
    # =============================================================

    def to_planner_contract(
        self,
        data: Union[dict, PlannerContract, Any],
        user_message: str = "",
    ) -> PlannerContract:
        """
        Validate and normalize input data into a typed PlannerContract with PlannerStep list.
        """
        if isinstance(data, PlannerContract):
            return data

        if not isinstance(data, dict):
            return PlannerContract(
                steps=[],
                user_message=user_message,
                metadata={"error": "Non-dictionary planner input"},
            )

        user_msg = data.get("user_message") or user_message
        metadata = dict(data.get("metadata", {})) if isinstance(data.get("metadata"), dict) else {}

        raw_steps = data.get("steps")
        normalized_steps: List[PlannerStep] = []

        if isinstance(raw_steps, list):
            for step in raw_steps:
                parsed_step = self._normalize_planner_step(step)
                if parsed_step is not None:
                    normalized_steps.append(parsed_step)
        elif "tool" in data and "action" in data:
            # Single-step dictionary representation
            single_step = self._normalize_planner_step(data)
            if single_step is not None:
                normalized_steps.append(single_step)

        return PlannerContract(
            steps=normalized_steps,
            user_message=str(user_msg),
            metadata=metadata,
        )

    def _normalize_planner_step(self, step: Any) -> Union[PlannerStep, None]:
        if isinstance(step, PlannerStep):
            return step

        if not isinstance(step, dict):
            return None

        tool = str(step.get("tool", "")).strip()
        action = str(step.get("action", "")).strip()

        if not tool:
            return None

        if not action:
            action = "implement" if tool == "code" else "execute"

        inp = str(step.get("input", "")).strip() if step.get("input") is not None else ""
        parameters = dict(step.get("parameters", {})) if isinstance(step.get("parameters"), dict) else {}
        context = dict(step.get("context", {})) if isinstance(step.get("context"), dict) else {}

        # Preserve extra keys in parameters if present
        known_keys = {"tool", "action", "input", "parameters", "context"}
        for k, v in step.items():
            if k not in known_keys:
                parameters[k] = v

        return PlannerStep(
            tool=tool,
            action=action,
            input=inp,
            parameters=parameters,
            context=context,
        )


    # =============================================================
    # Tool Step Contract
    # =============================================================

    def to_tool_step_contract(
        self,
        data: Union[dict, ToolStepContract, PlannerStep, Any],
    ) -> ToolStepContract:
        """
        Convert a PlannerStep or dict into a typed ToolStepContract.
        """
        if isinstance(data, ToolStepContract):
            return data

        if isinstance(data, PlannerStep):
            return ToolStepContract(
                tool=data.tool,
                action=data.action,
                input=data.input,
                parameters=dict(data.parameters),
                context=dict(data.context),
            )

        if isinstance(data, dict):
            tool = str(data.get("tool", "")).strip()
            action = str(data.get("action", "")).strip()
            inp = str(data.get("input", "")).strip() if data.get("input") is not None else ""
            parameters = dict(data.get("parameters", {})) if isinstance(data.get("parameters"), dict) else {}
            context = dict(data.get("context", {})) if isinstance(data.get("context"), dict) else {}

            known_keys = {"tool", "action", "input", "parameters", "context"}
            for k, v in data.items():
                if k not in known_keys:
                    parameters[k] = v

            return ToolStepContract(
                tool=tool,
                action=action,
                input=inp,
                parameters=parameters,
                context=context,
            )

        return ToolStepContract(
            tool="",
            action="",
            input=str(data) if data is not None else "",
        )

    # =============================================================
    # Tool Result Contract
    # =============================================================

    def to_tool_result_contract(
        self,
        data: Any,
        success: bool = True,
        message: str = "",
        error: Any = None,
    ) -> ToolResultContract:
        """
        Convert heterogeneous tool outputs (str, dict, bool, exception, etc.)
        into a canonical ToolResultContract.
        """
        if isinstance(data, ToolResultContract):
            return data

        if isinstance(data, Exception):
            return ToolResultContract(
                success=False,
                error=str(data),
                message=str(data),
                data=None,
            )

        if isinstance(data, dict):
            # If the dict explicitly indicates success / error:
            is_success = bool(data.get("success", success))
            msg = str(data.get("message", message or ""))
            err = data.get("error", error)

            payload_data = data.get("data", data)
            metadata = dict(data.get("metadata", {})) if isinstance(data.get("metadata"), dict) else {}

            known = {"success", "message", "error", "data", "metadata"}
            for k, v in data.items():
                if k not in known:
                    metadata[k] = v

            return ToolResultContract(
                success=is_success,
                message=msg,
                error=err,
                data=payload_data,
                metadata=metadata,
            )

        if isinstance(data, str):
            return ToolResultContract(
                success=success,
                message=message or data,
                error=error,
                data=data,
            )

        if isinstance(data, bool):
            return ToolResultContract(
                success=data,
                message=message,
                error=error,
                data=data,
            )

        return ToolResultContract(
            success=success if error is None else False,
            message=message,
            error=error,
            data=data,
        )

    # =============================================================
    # Memory Contract
    # =============================================================

    def to_memory_contract(
        self,
        data: Union[dict, MemoryContract, Any],
        default_action: str = "get",
        default_key: str = "",
        default_category: str = "general",
    ) -> MemoryContract:
        """
        Convert data/dict into a typed MemoryContract.
        """
        if isinstance(data, MemoryContract):
            return data

        if isinstance(data, dict):
            action = str(data.get("action", default_action)).strip()
            key = str(data.get("key", default_key)).strip()
            value = data.get("value")
            category = str(data.get("category", default_category)).strip()

            return MemoryContract(
                action=action,
                key=key,
                value=value,
                category=category,
            )

        return MemoryContract(
            action=default_action,
            key=str(data or default_key),
            category=default_category,
        )
