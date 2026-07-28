

import os
from functools import lru_cache


@lru_cache(maxsize=512)
def _load_file_witout_comments_cached(abs_file_name, mtime_ns, size):
    file_content = ""
    with open(abs_file_name, "r", encoding="utf-8") as f:
        contents = f.readlines()
        for x in contents:
            file_content += x.split("--")[0].split("\r\n")[0].split("\n")[0] + " "

    file_content = file_content.replace("\t", "  ")
    file_content = file_content.replace("(", " ( ")
    file_content = file_content.replace(")", " ) ")
    file_content = file_content.replace(";", " ; ")
    file_content = file_content.replace(":", " : ")
    file_content = file_content.replace(": =", " := ")
    file_content = file_content.lower()
    file_content = ' '.join(file_content.split())
    file_content = file_content.replace(" slv ", " std_logic_vector ")
    file_content = file_content.replace(" sl ", " std_logic ")
    return file_content


def load_file_witout_comments(FileName):
    abs_file_name = os.path.abspath(FileName)
    file_stat = os.stat(abs_file_name)
    return _load_file_witout_comments_cached(
        abs_file_name,
        file_stat.st_mtime_ns,
        file_stat.st_size,
    )