def parse_repository_analyzer(task):

    task_lower = task.lower().strip()


    project_keywords = [

        "proje",
        "project",
        "repository",
        "repo",
        "mimari",
        "architecture",
        "sistem",
        "uygulama"

    ]


    analysis_keywords = [

        "analiz",
        "incele",
        "değerlendir",
        "gözden geçir",
        "analyze",
        "review"

    ]


    has_project = any(

        word in task_lower

        for word in project_keywords

    )


    has_analysis = any(

        word in task_lower

        for word in analysis_keywords

    )



    if has_project and has_analysis:


        return {

            "steps": [

                {

                    "tool": "repository_analyzer",

                    "action": "analyze",

                    "input": task

                }

            ]

        }



    return None