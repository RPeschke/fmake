


def load_file_witout_comments(FileName):
    file_content = ""
    with open(FileName, "r", encoding="utf-8") as f:
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