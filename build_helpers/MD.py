import re
from pathlib import Path

from markdown_it import MarkdownIt


md = MarkdownIt()


def read_file(filename):
    return Path(filename).read_text(encoding="utf-8")


def markdown_anchor(text):
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"\s+", "-", text)


def get_outline_md(content):
    tokens = md.parse(content)

    outline = []

    for i, token in enumerate(tokens):
        if token.type != "heading_open":
            continue

        level = int(token.tag[1])
        title = tokens[i + 1].content
        anchor = markdown_anchor(title)

        outline.append((level, title, anchor))

    return outline


def md_concat(file_list):
    toc = []
    body = []

    for filename in file_list:
        content = read_file(filename)

        for level, title, anchor in get_outline_md(content):
            indent = "  " * min(level - 1, 2)
            toc.append(f"{indent}- [{title}](#{anchor})")

        body.append(content)

    return "\n".join(toc) + "\n\n" + "\n\n".join(body)

