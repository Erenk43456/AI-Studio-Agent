def parse_code_analyzer(task):

    keywords = [

        "analyze code",
        "analyze this code",
        "review code",
        "check this code",
        "find bugs",
        "code analysis"

    ]


    for word in keywords:

        if word in task:

            return {

                "tool": "code_analyzer",

                "code": task.replace(
                    word,
                    ""
                ).strip()

            }


    return None