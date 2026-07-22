def parse_memory(task):

    task = task.lower().strip()


    # Memory Get

    if (
        "adım ne" in task
        or "ismim ne" in task
        or "ben kimim" in task
    ):

        return {

            "tool": "memory_get",

            "key": "isim"

        }



    if "favori oyunum ne" in task:


        return {

            "tool": "memory_get",

            "key": "favori_oyun"

        }



    # Memory Save


    if task.startswith(
        "benim adım "
    ):


        return {

            "tool": "memory_save",

            "key": "isim",

            "value": task.replace(
                "benim adım",
                ""
            ).strip(),

            "category": "personal"

        }




    if "favori oyunum" in task:


        value = task.replace(
            "favori oyunum",
            ""
        ).strip()



        return {

            "tool": "memory_save",

            "key": "favori_oyun",

            "value": value,

            "category": "preference"

        }





    if (
        "öğreniyorum" in task
        or "ogreniyorum" in task
    ):


        value = task.replace(
            "öğreniyorum",
            ""
        ).replace(
            "ogreniyorum",
            ""
        ).strip()



        return {

            "tool": "memory_save",

            "key": "öğreniyor",

            "value": value,

            "category": "interest"

        }



    return None