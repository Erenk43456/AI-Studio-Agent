def parse_code_analyzer(task):


    task_lower = task.lower()



    analysis_keywords = [

        "analiz et",
        "analiz",
        "incele",
        "kontrol et",
        "değerlendir",
        "hata bul",
        "bug bul",
        "nasıl çalışıyor",
        "ne yapıyor",
        "ne işe yarıyor",
        "açıkla",

        "analyze",
        "review",
        "check",
        "find bugs",
        "code analysis"

    ]





    file_target_keywords = [

        ".py",
        "dosya",
        "file",
        "class",
        "function",
        "method",
        "fonksiyon",
        "sınıf"

    ]





    component_keywords = [

        "agent",
        "tool",
        "memory",
        "llm",
        "planner",
        "orchestrator",
        "parser"

    ]





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






    has_analysis = any(

        word in task_lower

        for word in analysis_keywords

    )



    if not has_analysis:

        return None






    has_file_target = any(

        word in task_lower

        for word in file_target_keywords

    )



    has_component = any(

        word in task_lower

        for word in component_keywords

    )



    has_project = any(

        word in task_lower

        for word in project_keywords

    )





    #
    # Proje analizleri repository analyzer'a gider
    #

    if has_project and not has_file_target:


        return None





    #
    # Dosya/component analizleri
    #

    if has_file_target or has_component:


        filename = ""


        for part in task.split():

            clean = (

                part
                .replace("'", "")
                .replace('"', "")
                .replace("`", "")
            )


            if clean.endswith(".py"):

                filename = clean

                break





        return {

            "steps":[

                {

                    "tool":"code_analyzer",

                    "action":"analyze",

                    "filename":filename,

                    "content":"",

                    "input":task

                }

            ]

        }





    return None