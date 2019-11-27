import datetime
import os


def get_lines_above_that_start_with_comment_sign(source_code, i):
    doc = ""
    j = i - 1
    while j >= 0 and source_code[j].startswith("//"):
        doc = source_code[j] + doc
        j -= 1
    return doc


def get_lines_below_that_start_with_sign(source_code, i, sign):
    lines = ""
    j = i + 1
    while j < len(source_code):
        lines += source_code[j]
        if source_code[j].startswith(sign):
            break
        j += 1
    return lines


def mark_code(s):
    return f"<pre><code>{s}</code></pre>"


def generate_index_file(docs_path, path, source_code_structure):
    site_name = f"{path} docs"
    with open(os.path.join(docs_path, "index.html"), "w") as index_file:
        index_file.write(
            f"""
<h1>{site_name}</h1>
<h1>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</h1>
<h1>version 1.0.0</h1>
<h1>{os.path.basename((os.getcwd()))}</h1>
<div><a href="{os.path.join(os.getcwd(),docs_path,path,"content.html")}">content</a></div>
"""
        )
