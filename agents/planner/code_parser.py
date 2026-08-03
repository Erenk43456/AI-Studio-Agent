def parse_code(task):

    keywords = [

        "ekle",
        "oluştur",
        "geliştir",
        "implement",
        "refactor",
        "entegrasyon",
        "sistemine",
        "agent",
        "tool",
        "framework",
        "özellik"

    ]


    task_lower = task.lower()


    score = 0


    for keyword in keywords:

        if keyword in task_lower:

            score += 1



    if score >= 2:

        return {

            "steps": [

                {
                    "tool": "repository_analyzer",
                    "action": "analyze",
                    "input": task
                },

                {
                    "tool": "code_analyzer",
                    "action": "analyze",
                    "input": task
                },

                {
                    "tool": "code",
                    "action": "implement",
                    "input": task
                }

            ]

        }


    return None