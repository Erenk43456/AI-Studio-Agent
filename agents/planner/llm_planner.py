import json
import re


def clean_json(text):

    if not text:
        return "{}"

    text = text.strip()

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

    return "{}"


def format_tools(tool_descriptions):

    if not tool_descriptions:
        return "No tool information available."

    result = ""

    for tool in tool_descriptions:

        result += f"""
Tool:
{tool.get("name")}

Description:
{tool.get("description")}

Purpose:
{tool.get("purpose")}

---
"""

    return result


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

Do semantic reasoning.

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


Tool selection guidance:

chat:
Use for normal conversation, greetings, questions that do not require tools.

code_analyzer:
Use when the user wants to inspect, review, understand or find problems in existing code files.

repository_analyzer:
Use when the user wants to understand the whole project structure, architecture or repository.

code:
Use for software engineering tasks:

- adding features
- refactoring
- improving architecture
- fixing implementation problems
- changing agent behavior

file:
Use for direct file operations requested by the user.

Important:

Do not select tools using exact words.
Understand the meaning.

Never invent tools.

Never return empty steps.

Always return at least one step.


Examples:

User:
"Merhaba"

Output:

{{
    "steps": [
        {{
            "tool": "chat",
            "action": "chat",
            "input": "Merhaba"
        }}
    ]
}}


User:
"agents/tool_agent.py dosyasını analiz et"

Output:

{{
    "steps": [
        {{
            "tool": "code_analyzer",
            "action": "analyze",
            "filename": "agents/tool_agent.py",
            "input": "Analyze file"
        }}
    ]
}}


User:
"AI-Studio projesinin mimarisini incele"

Output:

{{
    "steps": [
        {{
            "tool": "repository_analyzer",
            "action": "analyze",
            "input": "Analyze repository architecture"
        }}
    ]
}}


User:
"Memory sistemini geliştir"

Output:

{{
    "steps": [
        {{
            "tool": "code",
            "action": "implement",
            "input": "Improve memory system"
        }}
    ]
}}


User request:

{task}
"""

    try:

        response = llm.generate(
            prompt,
            temperature=0
        )

        print(
            "\n===== RAW PLANNER RESPONSE ====="
        )

        print(response)

        print(
            "================================\n"
        )

        cleaned = clean_json(
            response
        )

        plan = json.loads(
            cleaned
        )

        if "steps" not in plan:

            if "tool" in plan:

                plan = {
                    "steps": [
                        plan
                    ]
                }

            else:

                plan = {
                    "steps": [
                        {
                            "tool": "chat",
                            "action": "chat",
                            "input": task
                        }
                    ]
                }

        if not plan["steps"]:

            plan = {
                "steps": [
                    {
                        "tool": "chat",
                        "action": "chat",
                        "input": task
                    }
                ]
            }

        return plan

    except Exception as error:

        print(
            "Planner JSON error:",
            error
        )

        return {
            "steps": [
                {
                    "tool": "chat",
                    "action": "chat",
                    "input": task
                }
            ]
        }