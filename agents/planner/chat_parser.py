def parse_chat(task):

    text = task.lower()


    keywords = [

        "nedir",
        "ne yapıyor",
        "nasıl çalışır",
        "nasıl çalışıyor",
        "açıkla",
        "bilgi ver",
        "anlat",
        "hakkında bilgi",
        "ne işe yarar",
        "amacı ne",
        "görevi ne"

    ]


    for keyword in keywords:

        if keyword in text:

            return {

                "tool": "chat",

                "message": task

            }


    return None