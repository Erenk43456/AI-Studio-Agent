import re



def parse_formatter(task):


    keywords = [
        "formatla",
        "format",
        "düzenle",
        "girintiyi düzelt",
        "kodu düzelt"
    ]



    is_formatter_request = False



    for word in keywords:

        if word in task:

            is_formatter_request = True

            break



    if not is_formatter_request:

        return None





    code = task



    for word in keywords:

        code = code.replace(
            word,
            ""
        )



    code = code.strip()





    match = re.search(

        r"```(?:python)?\s*(.*?)```",

        code,

        re.DOTALL

    )



    if match:


        code = match.group(1).strip()





    return {

        "tool": "formatter",

        "action": "code",

        "code": code

    }