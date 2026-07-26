def parse_code_repair(task):

    keywords = [
        "kodu düzelt",
        "kodumu düzelt",
        "hataları düzelt",
        "bug düzelt",
        "repair code"
    ]


    for word in keywords:

        if word in task:

            return {

                "tool": "code_repair",

                "code": task.replace(
                    word,
                    ""
                ).strip()

            }


    return None