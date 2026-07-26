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







def create_llm_plan(
    llm,
    task
):


    prompt = f"""

You are an AI agent planner.

Return JSON only.

You can create single-step or multi-step plans.

Available tools:

calculator:
Math operations.

memory_save:
Save information.

memory_get:
Retrieve information.

file:
File operations.

code_analyzer:
Analyze source code.

code_repair:
Fix programming errors.

formatter:
Format code.

chat:
Normal conversation.


Rules:

- Return only valid JSON.
- Never add explanations.
- For simple requests use one step.
- For complex tasks create multiple steps.
- Steps must be executed in order.
- Always include required parameters.
- For code tools include the full source code in the "code" field.
- Never leave required fields empty.

Important:

- Never modify user input.
- Preserve the original code exactly.
- Put the original source code in the "code" field or "input" field.
- Do not fix, format, or rewrite code inside the plan.


JSON formats:

Single tool:

{{
    "steps": [
        {{
            "tool": "chat",
            "input": "message"
        }}
    ]
}}


Multiple tools:

{{
    "steps": [
        {{
            "tool": "code_analyzer",
            "input": "analyze code"
        }},
        {{
            "tool": "code_repair",
            "input": "fix code"
        }}
    ]
}}


User:

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



        # eski sistem uyumluluğu

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