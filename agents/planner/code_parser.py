def parse_code(task):

    task_lower = task.lower()


    score = 0



    #
    # Development commands
    #

    keywords = [

        "ekle",
        "oluştur",
        "geliştir",
        "implement",
        "refactor",
        "entegrasyon",
        "özellik",
        "sistem",
        "framework",

        "değiştir",
        "düzenle",
        "güncelle",
        "iyileştir",
        "optimize",
        "düzelt",
        "yenile",

        "mimari",
        "tasarla",
        "genişlet",
        "upgrade",
        "revize"

    ]




    for keyword in keywords:

        if keyword in task_lower:

            score += 1





    #
    # Actual python file target
    #

    if ".py" in task_lower:

        score += 2





    #
    # Description / analysis requests
    #

    analysis_keywords = [

        "ne yapıyor",
        "ne işe yarar",
        "nasıl çalışır",
        "açıkla",
        "anlat",
        "analiz et",
        "incele",
        "bak",
        "göster",
        "nedir"

    ]




    for keyword in analysis_keywords:

        if keyword in task_lower:

            score -= 3





    #
    # Just a development goal
    #

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