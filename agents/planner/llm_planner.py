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

--------------------

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

You are an AI planner.

Your job:
Convert the user request into an execution plan.

Return ONLY valid JSON.

No markdown.
No explanations.



Available tools:

{tools_text}



Rules:

1.
Simple conversation:
Use:

{{
 "steps":[
  {{
   "tool":"chat",
   "action":"chat",
   "input":"user message"
  }}
 ]
}}



2.
Code analysis:
Use code_analyzer.



3.
Repository analysis:
Use repository_analyzer.



4.
Software development:
Use code.



5.
File operations:
Use file.



6.
Never invent tools.

7.
Never return empty steps.

8.
Always include at least one step.



Examples:



User:
"merhaba"


Output:

{{
 "steps":[
  {{
   "tool":"chat",
   "action":"chat",
   "input":"merhaba"
  }}
 ]
}}



User:
"agents/tool_agent.py analiz et"


Output:

{{
 "steps":[
  {{
   "tool":"code_analyzer",
   "action":"analyze",
   "filename":"agents/tool_agent.py",
   "input":"analyze file"
  }}
 ]
}}



User:
"projeye authentication ekle"


Output:

{{
 "steps":[
  {{
   "tool":"code",
   "action":"implement",
   "input":"Add authentication system"
  }}
 ]
}}



User request:

{task}

"""



    try:


        response = llm.generate(

            prompt,

            max_tokens=1024,

            temperature=0.1

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

                    "steps":[

                        plan

                    ]

                }


            else:


                plan = {

                    "steps":[

                        {

                            "tool":"chat",

                            "action":"chat",

                            "input":task

                        }

                    ]

                }



        if not plan["steps"]:


            plan = {

                "steps":[

                    {

                        "tool":"chat",

                        "action":"chat",

                        "input":task

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

            "steps":[

                {

                    "tool":"chat",

                    "action":"chat",

                    "input":task

                }

            ]

        }