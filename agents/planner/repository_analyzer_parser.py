def parse_repository_analyzer(task):

    task = task.lower().strip()

    keywords = [
        "repository analyze",
        "analyze repository",
        "analyze this repository",
        "analyze repo",
        "repository analizi",
        "repo analiz",
        "repo incele",
        "repository incele",
        "depo analizi",
        "repository analiz et",
        "repo analiz et",
        "projeyi analiz et",
    ]

    for word in keywords:

        if word in task:

            return {
                "tool": "repository_analyzer",
                "action": "analyze"
            }

    return None
