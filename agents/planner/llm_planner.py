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
   Retrieves persistent user memory.

   Required field:
   - key

   Example:

   {{
       "tool": "memory",
       "action": "get",
       "key": "user_name"
   }}

2. save
   Stores persistent user memory.

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

For memory retrieval, ONLY use:

"action": "get"

Never use:

- query
- retrieve
- recall
- search
- lookup
- read
- fetch

For memory saving, ONLY use:

"action": "save"

Never use:

- remember
- store
- write
- add

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

Examples:

{{
    "tool": "project_memory",
    "action": "overview"
}}

{{
    "tool": "project_memory",
    "action": "architecture"
}}

{{
    "tool": "project_memory",
    "action": "files"
}}

{{
    "tool": "project_memory",
    "action": "file",
    "path": "agents/chat_agent.py"
}}

{{
    "tool": "project_memory",
    "action": "search",
    "query": "memory"
}}

{{
    "tool": "project_memory",
    "action": "context",
    "query": "memory",
    "limit": 5
}}

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

Use this when the user wants to modify software.

Example:

{{
    "tool": "code",
    "action": "implement",
    "input": "Fix the memory system"
}}

--------------------------------------------------
CHAT
--------------------------------------------------

Tool name:
chat

Allowed action:

- chat

Example:

{{
    "tool": "chat",
    "action": "chat",
    "input": "Hello"
}}


==================================================
TOOL SELECTION RULES
==================================================

chat:
Use ONLY for normal conversation, greetings, casual discussion, general questions, or questions that cannot be answered by another available tool.

memory:
Use when the user asks about persistent personal information, remembered facts, preferences, or asks the system to remember something.

Examples:

- "Benim adım ne?"
- "What is my name?"
- "Beni hatırlıyor musun?"
- "Do you remember me?"
- "Favori oyunum ne?"
- "What is my favorite game?"
- "Benim hakkımda ne biliyorsun?"
- "What do you know about me?"

Do NOT use chat when the answer can be obtained from memory.

For a known personal fact, prefer a specific memory key.

For example:

"Benim adım ne?"

must become:

{{
    "tool": "memory",
    "action": "get",
    "key": "user_name"
}}

The Turkish and English versions of the same request MUST produce the same canonical tool action.

--------------------------------------------------

code_analyzer:
Use when the user wants to inspect, review, understand, explain, diagnose, or find problems in EXISTING SOURCE CODE.

Examples:

- "agents/chat_agent.py dosyasını analiz et"
- "Analyze agents/chat_agent.py"
- "Bu dosyada hata var mı?"
- "Is there a bug in this file?"
- "Bu kod neden çalışmıyor?"
- "Why does this code fail?"

--------------------------------------------------

repository_analyzer:
Use when the user wants to inspect or understand the WHOLE PROJECT, repository structure, architecture, dependencies, agent relationships, memory architecture, or project organization.

Examples:

- "AI-Studio projesinin mimarisini analiz et"
- "Analyze the project architecture"
- "Memory sistemimiz nasıl çalışıyor?"
- "How does the memory architecture work?"
- "Agent sistemi nasıl organize edilmiş?"
- "How is the agent system organized?"

--------------------------------------------------

project_memory:
Use when the answer requires information already stored in the project's persistent project memory.

Examples:

- "Projede hangi dosyalar var?"
- "What files are in the project?"
- "agents/chat_agent.py hakkında project memory'de ne var?"
- "What does project memory know about agents/chat_agent.py?"
- "Projenin mimarisi hakkında kayıtlı bilgiyi getir."
- "Show the stored project architecture."

--------------------------------------------------

code:
Use when the user wants to CHANGE, IMPLEMENT, FIX, REFACTOR, IMPROVE, or EXTEND the software.

Examples:

- "Memory sistemini geliştir"
- "Improve the memory system"
- "Memory sistemindeki hatayı düzelt"
- "Fix the memory system"
- "Agent sistemini daha modüler hale getir"
- "Make the agent system more modular"
- "Bu özelliği ekle"
- "Add this feature"
- "Bu kodu refactor et"
- "Refactor this code"

IMPORTANT:

There is a critical difference between ANALYZING and CHANGING.

If the user wants to understand, inspect, explain, review, or diagnose existing code:

→ use code_analyzer or repository_analyzer.

If the user wants to modify, fix, improve, implement, refactor, or extend the software:

→ use code.

If the user asks about persistent personal information:

→ use memory.

If the user asks about the project's stored architecture or files:

→ use project_memory.

If the user asks a normal conversational question:

→ use chat.

Never ask the user for a filename when the repository analyzer can inspect the project and identify the relevant files.

Never use chat as a fallback when the request is clearly a software development task.

Always prefer a specialized tool over chat when a specialized tool can perform the requested task.

Do not select tools using exact words.
Understand the meaning.

Never invent tools.

Never invent actions.

Always use the exact action names defined in TOOL CONTRACTS.

Never return empty steps.

Always return at least one step.


==================================================
EXECUTION PLAN
==================================================

Create the smallest valid execution plan.

Do not create unnecessary steps.

The output MUST have this structure:

{{
    "steps": [
        {{
            "tool": "...",
            "action": "...",
            ...
        }}
    ]
}}


==================================================
EXAMPLES
==================================================

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
"Hello"

Output:

{{
    "steps": [
        {{
            "tool": "chat",
            "action": "chat",
            "input": "Hello"
        }}
    ]
}}


User:
"Benim adım ne?"

Output:

{{
    "steps": [
        {{
            "tool": "memory",
            "action": "get",
            "key": "user_name"
        }}
    ]
}}


User:
"What is my name?"

Output:

{{
    "steps": [
        {{
            "tool": "memory",
            "action": "get",
            "key": "user_name"
        }}
    ]
}}


User:
"Benim adım Eren"

Output:

{{
    "steps": [
        {{
            "tool": "memory",
            "action": "save",
            "key": "user_name",
            "value": "Eren",
            "category": "personal"
        }}
    ]
}}


User:
"My name is Eren"

Output:

{{
    "steps": [
        {{
            "tool": "memory",
            "action": "save",
            "key": "user_name",
            "value": "Eren",
            "category": "personal"
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
"Analyze agents/tool_agent.py"

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
"Analyze the AI-Studio project architecture"

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


User:
"Fix the memory system"

Output:

{{
    "steps": [
        {{
            "tool": "code",
            "action": "implement",
            "input": "Fix the memory system"
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