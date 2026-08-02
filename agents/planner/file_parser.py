import re




def parse_file(task):


    text = task.lower()



    filename = extract_filename(task)


    if not filename:

        return None





    #
    # CREATE
    #

    if any(word in text for word in [

        "oluştur",
        "yarat",
        "meydana getir"

    ]):


        return {

            "tool": "file",

            "action": "create",

            "filename": filename,

            "content": ""

        }








    #
    # READ
    #

    if any(word in text for word in [

        "oku",
        "göster",
        "söyle",
        "içeriğini",
        "bak",
        "incele",
        "görüntüle"

    ]):


        return {

            "tool": "file",

            "action": "read",

            "filename": filename

        }









    #
    # WRITE / EDIT
    #

    if any(word in text for word in [

        "düzenle",
        "güncelle",
        "yaz",
        "ekle",
        "değiştir",
        "sil"

    ]):


        return {


            "steps": [

                {

                    "tool": "file",

                    "action": "read",

                    "filename": filename

                },


                {

                    "tool": "file",

                    "action": "write",

                    "filename": filename,

                    "content": "",

                    "input": task

                }

            ]

        }






    return None











def extract_filename(task):


    match = re.search(

        r"[\w/\\.-]+\.py",

        task

    )


    if match:


        return match.group(0).replace(

            "\\",

            "/"

        )



    return None