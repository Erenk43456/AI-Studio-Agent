import re





def parse_file(task):


    text = task.lower()



    filename = extract_filename(task)


    if not filename:

        return None






    #
    # CREATE EMPTY FILE
    #

    if any(word in text for word in [

        "boş dosya oluştur",
        "dosya oluştur",
        "dosya yarat"

    ]):


        return {

            "tool": "file",

            "action": "create",

            "filename": filename,

            "content": ""

        }









    #
    # READ FILE
    #

    if any(word in text for word in [

        "oku",
        "göster",
        "içeriğini göster",
        "içeriğini oku",
        "bak",
        "görüntüle"

    ]):



        return {

            "tool": "file",

            "action": "read",

            "filename": filename

        }









    #
    # DELETE FILE
    #

    if any(word in text for word in [

        "dosyayı sil",
        "dosya sil"

    ]):



        return {

            "tool": "file",

            "action": "delete",

            "filename": filename

        }









    #
    # MOVE / COPY gibi gerçek file işlemleri
    #

    if any(word in text for word in [

        "taşı",
        "kopyala"

    ]):


        return {

            "tool": "file",

            "action": "manage",

            "filename": filename

        }







    #
    # Kod değiştirme işlemleri burada yakalanmaz.
    # CodeParser'a bırakılır.
    #

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