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



    # Mesaj doğrudan selamlama ise çalışsın

    if task in greetings:

        return {

            "tool": "chat",

            "message": task

        }



    # kısa selamlama cümleleri

    words = task.split()



    if len(words) <= 3:


        if any(

            word in greetings

            for word in words

        ):

            return {

                "tool": "chat",

                "message": task

            }



    return None