import re



def parse_calculator(task):

    task = task.lower().strip()


    # Direkt matematik:
    # 15+20
    # 10 * 5

    expression = re.search(
        r"(\d+)\s*([\+\-\*/])\s*(\d+)",
        task
    )


    if expression:


        a = int(
            expression.group(1)
        )


        operator = expression.group(2)


        b = int(
            expression.group(3)
        )


        operations = {

            "+": "add",
            "-": "subtract",
            "*": "multiply",
            "/": "divide"

        }


        return {

            "tool": "calculator",

            "operation": operations[operator],

            "numbers": [

                a,
                b

            ]

        }





    # Türkçe komutlar

    numbers = re.findall(
        r"\d+",
        task
    )


    math_words = [

        "topla",
        "ekle",
        "arttır",
        "artir",

        "çıkar",
        "cikar",
        "eksi",

        "çarp",
        "carp",
        "kat",

        "böl",
        "bol"

    ]



    if (

        len(numbers) >= 2

        and any(
            word in task
            for word in math_words
        )

    ):


        operation = "add"



        if (

            "çıkar" in task
            or "cikar" in task
            or "eksi" in task

        ):

            operation = "subtract"



        elif (

            "çarp" in task
            or "carp" in task
            or "kat" in task

        ):

            operation = "multiply"



        elif (

            "böl" in task
            or "bol" in task

        ):

            operation = "divide"



        return {

            "tool": "calculator",

            "operation": operation,

            "numbers": [

                int(numbers[0]),
                int(numbers[1])

            ]

        }



    return None