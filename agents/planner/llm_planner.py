import json
import re


def clean_json(
    text
):

    if not isinstance(
        text,
        str
    ):

        return "{}"

    text = text.strip()

    if not text:

        return "{}"

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    text = text.strip()

    match = re.search(
        r"\{[\s\S]*\}",
        text
    )

    if match:

        return match.group()

    return "{}"


def format_tools(
    tool_descriptions
):

    if not tool_descriptions:

        return "No tool information available."

    result = ""

    for tool in tool_descriptions:

        if not isinstance(
            tool,
            dict
        ):

            continue

        result += f"""
Tool:
{tool.get("name")}

Description:
{tool.get("description")}

Purpose:
{tool.get("purpose")}

---
"""

    if not result:

        return "No tool information available."

    return result


def validate_plan(
    plan,
    tool_descriptions=None,
):
    if not isinstance(plan, dict):
        return False

    steps = plan.get("steps")

    if not isinstance(steps, list):
        return False

    if not steps:
        return False

    available_tools = None

    if tool_descriptions is not None:
        available_tools = {
            tool.get("name")
            for tool in tool_descriptions
            if isinstance(tool, dict)
            and isinstance(tool.get("name"), str)
            and tool.get("name").strip()
        }

    for step in steps:

        if not isinstance(step, dict):
            return False

        tool = step.get("tool")
        action = step.get("action")

        if not isinstance(tool, str) or not tool.strip():
            return False

        if not isinstance(action, str) or not action.strip():
            return False

        if (
            available_tools is not None
            and tool not in available_tools
        ):
            return False

    return True


def create_llm_plan(
    llm,
    task,
    tool_descriptions=None
):

    tools_text = format_tools(
        tool_descriptions
    )

    prompt = f"""
You are the central reasoning engine of an autonomous AI agent.

Your task is to understand the user's intent and create an execution plan.

You are NOT a keyword matcher.

Perform semantic reasoning.

Choose the most appropriate tool based on:

- user intent
- available tool capabilities
- requested operation

Always choose the minimum number of tools required.

Return JSON only.
No markdown.
No explanations.

Available tools:

{tools_text}


==================================================
TOOL CONTRACTS
==================================================

You MUST follow these tool contracts exactly.

You MUST NOT invent tool names.

You MUST NOT invent actions.

You MUST NOT rename actions.

You MUST NOT use synonyms for actions.

--------------------------------------------------
MEMORY TOOL
--------------------------------------------------

Tool name:
memory

Allowed actions:

1. get

Required field:
- key

Example:

{{
    "tool": "memory",
    "action": "get",
    "key": "user_name"
}}

2. save

Required fields:
- key
- value

Optional field:
- category

Example:

{{
    "tool": "memory",
    "action": "save",
    "key": "user_name",
    "value": "Eren",
    "category": "personal"
}}

IMPORTANT:

For memory retrieval ONLY use:

"action": "get"

For memory saving ONLY use:

"action": "save"


--------------------------------------------------
PROJECT MEMORY TOOL
--------------------------------------------------

Tool name:
project_memory

Allowed actions:

- overview
- file
- files
- architecture
- search
- context


--------------------------------------------------
CODE ANALYZER
--------------------------------------------------

Tool name:
code_analyzer

Allowed action:

- analyze

Example:

{{
    "tool": "code_analyzer",
    "action": "analyze",
    "filename": "agents/chat_agent.py",
    "input": "Analyze file"
}}


--------------------------------------------------
REPOSITORY ANALYZER
--------------------------------------------------

Tool name:
repository_analyzer

Allowed action:

- analyze

Example:

{{
    "tool": "repository_analyzer",
    "action": "analyze",
    "input": "Analyze repository architecture"
}}


--------------------------------------------------
CODE
--------------------------------------------------

Tool name:
code

Allowed action:

- implement

Use this when the user wants to:

- modify
- fix
- implement
- improve
- refactor
- extend
- change

existing software.

Example:

{{
    "tool": "code",
    "action": "implement",
    "input": "Fix the memory system"
}}


==================================================
TOOL SELECTION RULES
==================================================

memory:

Use for persistent user information.

code_analyzer:

Use when the user wants to inspect,
review, understand, explain, diagnose,
or analyze EXISTING SOURCE CODE.

repository_analyzer:

Use when the user wants to inspect
the WHOLE PROJECT, architecture,
dependencies, repository structure,
or agent relationships.

project_memory:

Use when the answer requires information
already stored in persistent project memory.

code:

Use when the user wants to CHANGE software.

This includes:

- fix
- implement
- add
- improve
- refactor
- modify
- extend
- develop

CRITICAL:

If the user wants to MODIFY software,
NEVER use chat.

If the user wants to FIX software,
NEVER use chat.

If the user wants to IMPLEMENT software,
NEVER use chat.

If the user wants to REFACTOR software,
NEVER use chat.

Always use:

"tool": "code"

with:

"action": "implement"

Never invent tools.

Never invent actions.

Never return empty steps.

Always return at least one step.


==================================================
EXECUTION PLAN
==================================================

Create the smallest valid execution plan.

The output MUST have this structure:

{{
    "steps": [
        {{
            "tool": "...",
            "action": "...",
            "input": "..."
        }}
    ]
}}


==================================================
USER REQUEST
==================================================

{task}
"""

    try:

        response = llm.generate(
            prompt,
            max_tokens=1200,
            temperature=0
        )

    except Exception as error:

        print(
            "Planner LLM error:",
            error
        )

        return None

    # =========================================================
    # API error response
    # =========================================================

    if isinstance(
        response,
        dict
    ):

        print(
            "Planner received API error:",
            response
        )

        return None

    # =========================================================
    # Unexpected response
    # =========================================================

    if not isinstance(
        response,
        str
    ):

        print(
            "Planner received unexpected response type:",
            type(response)
        )

        return None

    print(
        "\n===== RAW PLANNER RESPONSE ====="
    )

    print(
        response
    )

    print(
        "================================\n"
    )

    # =========================================================
    # Parse JSON
    # =========================================================

    try:

        cleaned = clean_json(
            response
        )

        plan = json.loads(
            cleaned
        )


    except Exception as error:

        print(
            "Planner JSON error:",
            error
        )

        return None

    if not isinstance(
        plan,
        dict
    ):

        return None

    # =========================================================
    # Normalize single-step response
    # =========================================================

    if "steps" not in plan:

        if "tool" in plan:

            plan = {
                "steps": [
                    plan
                ]
            }

        else:

            return None

    steps = plan.get(
        "steps"
    )

    if not isinstance(
        steps,
        list
    ):

        return None

    if not steps:

        return None


    # =========================================================
    # Validate execution plan
    # =========================================================

    if not validate_plan(
        plan,
        tool_descriptions,
    ):

        print(
            "Planner returned an invalid execution plan."
        )

        return None

    return plan