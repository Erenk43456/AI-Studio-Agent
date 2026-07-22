def parse_greeting(task):

    task = task.lower().strip()


    greetings = [

        "merhaba",
        "selam",
        "hey",
        "hi",
        "hello",
        "nasılsın",
        "teşekkür",
        "sağol"

    ]


    if any(

        word in task

        for word in greetings

    ):


        return {

            "tool": "chat",

            "message": task

        }



    return None