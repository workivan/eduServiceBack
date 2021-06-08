import docx
import re


def get_content_from_file(file):
    doc = docx.Document(file)
    body = "\n".join([part.text for part in doc.paragraphs[1:]])
    return {
        "title":
            re.sub("docx", "", file.name),
        "body": body
    }
