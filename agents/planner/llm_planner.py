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

Available tools:

calculator:
Math operations.

memory_save:
Save information.

memory_get:
Retrieve information.

file:
File operations.

chat:
Normal conversation.


Rules:

- Return only JSON.
- No explanations.
- Use chat for normal conversations.


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



        if "tool" not in plan:

            plan["tool"] = "chat"



        return plan




    except Exception:


        return {

            "tool": "chat",

            "message": task

        }