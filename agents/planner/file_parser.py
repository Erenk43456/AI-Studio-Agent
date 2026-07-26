def parse_file(task):


    if "oluştur" in task or "oluştur" in task:

        return {

            "tool": "file",

            "action": "create",

            "filename": extract_filename(task),

            "content": ""

        }


    if "oku" in task:

        return {

            "tool": "file",

            "action": "read",

            "filename": extract_filename(task)

        }


    if "düzenle" in task or "güncelle" in task:

        return {

            "tool": "file",

            "action": "write",

            "filename": extract_filename(task),

            "content": ""

        }


    return None




def extract_filename(task):


    words = task.split()


    for word in words:

        if ".py" in word:

            return word.strip("., ")


    return None