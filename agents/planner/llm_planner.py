import json
import re



def clean_json(text):

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
        r"\{.*\}",
        text,
        re.DOTALL
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


        result += f"""

Tool name:
{tool.get("name")}


Description:
{tool.get("description")}


Purpose:
{tool.get("purpose")}


Safe:
{tool.get("safe")}


Modifies files:
{tool.get("modifies_files")}


----------------------------

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

You are an AI agent planner.

Your job is to decide which tools should execute a user request.

Return JSON only.

Available tools:

{tools_text}



Planning rules:

- Return only valid JSON.
- Never add explanations.
- For simple requests use one step.
- For complex tasks create multiple steps.
- Steps must execute in order.
- Select the correct high level agent/tool.
- Let specialized agents decide internal workflows.
- Do not expand agent workflows into individual tool calls.

File modification rules:

- If user says:
  add
  append
  insert
  modify
  change
  update
  replace
  fix
  edit

  You MUST use file read first.

- After reading a file, ALWAYS create a second step using file write.

- Never use write with empty content.

- When modifying a file:
  preserve existing content.
  only apply requested changes.

Example:

User:
"Add # TEST to app.py"

Correct plan:

{{
"steps":[
{{
"tool":"file",
"action":"read",
"filename":"app.py"
}},
{{
"tool":"file",
"action":"write",
"filename":"app.py",
"content":"<existing content + change>"
}}
]
}}


Wrong:

{{
"tool":"file",
"action":"write",
"content":""
}}

Tool selection rules:

- Choose tools based on their description and purpose.
- Do not use tools that are unrelated.
- Do not modify files unless the user explicitly requests changes.
- Analysis tools should be used before modification tools.

CodeAgent rules:

You are planning software engineering requests.


If the user request involves:

- new features
- architecture changes
- refactoring
- debugging
- improving existing code
- adding capabilities
- modifying agents, tools, memory, GUI or framework components


You MUST use the "code" tool.



Examples:

"Add message search to ChatManager"

"Improve memory architecture"

"Add plugin system"

"Refactor orchestrator"

"Implement authentication"



CODE tasks workflow:

The code tool is responsible for:

- understanding repository architecture
- analyzing affected files
- designing implementation
- producing modification instructions



For CODE tasks:

Return only:

{{
 "steps":[
   {{
    "tool":"code",
    "action":"implement",
    "input":"user request"
   }}
 ]
}}



Do NOT manually add:

- repository_analyzer
- code_analyzer
- file read
- file write


The CodeAgent controls the engineering workflow internally.

Wrong:

{{
"steps":[
{{
"tool":"repository_analyzer"
}}
]
}}


Correct:

{{
"steps":[
{{
"tool":"repository_analyzer"
}},
{{
"tool":"code_analyzer"
}},
{{
"tool":"code"
}},
{{
"tool":"file"
}}
]
}}

Implementation rules:

- After CodeAgent creates implementation plan:
- If files must be modified:
- Use code_writer tool.
- code_writer receives CodeAgent JSON output.
- Never use file write directly for software development.

The final goal is completing the user's request, not only explaining the repository.

Repository rules:

- Use repository_analyzer for repository structure analysis.
- Use code_analyzer for reviewing source code.
- Use code_repair only when fixing known errors.
- Use formatter only for formatting.

File tool rules:

- When using "file" tool always provide "action".
- When reading files always provide "filename".
- Never put file paths only inside "input".

File read example:

{{
    "tool": "file",
    "action": "read",
    "filename": "app/core/container.py",
    "input": "Read file"
}}


File write example:

{{
    "tool": "file",
    "action": "write",
    "filename": "app/core/container.py",
    "content": "new code",
    "input": "Update file"
}}


File create example:

{{
    "tool": "file",
    "action": "create",
    "filename": "new_file.py",
    "content": "file content",
    "input": "Create file"
}}


Memory rules:

- memory tools require explicit user intent.

Conversation rules:

- Normal conversation should use chat.

Important:

- Preserve user input.
- Do not rewrite user code.
- Do not invent missing files.
- Do not create unnecessary steps.



JSON format:

Single step:

{{
    "steps": [
        {{
            "tool": "tool_name",
            "action": "operation",
            "filename": "",
            "content": "",
            "input": "task description"
        }}
    ]
}}



Multiple steps:

{{
    "steps": [
        {{
            "tool": "first_tool",
            "action": "operation",
            "filename": "",
            "content": "",
            "input": "first task"
        }},
        {{
            "tool": "second_tool",
            "action": "operation",
            "filename": "",
            "content": "",
            "input": "second task"
        }}
    ]
}}



User request:

{task}

"""



    try:


        response = llm.generate(

            prompt

        )



        response = clean_json(

            response

        )


        plan = json.loads(

            response

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

                            "input": task

                        }

                    ]

                }



        return plan





    except Exception:


        return {

            "steps": [

                {

                    "tool": "chat",

                    "input": task

                }

            ]

        }