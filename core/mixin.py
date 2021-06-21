import mammoth
import re


def get_content_from_file(file):
    result = mammoth.convert_to_html(file)
    return {
        "title":
            re.sub("docx", "", file.name),
        "body": result.value
    }
