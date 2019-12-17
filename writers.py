import datetime
import os
import string


def generate_menu(original_docs_path, original_code_path):
    index_url = f"{original_docs_path}/index.html"
    content_url = f"{original_code_path}/content.html"
    indexed_url = f"{original_docs_path}/indexed.html"

    return f"""
                <div>
                    <a href="{index_url}">index</a>
                    <a href="{indexed_url}">alphabetic</a>
                    <a href="{content_url}">content</a>
                </div>
                <br>
                <form>
                    <input type="button" value="Go back!" onclick="history.back()">
                </form>
              """


def generate_index_file(original_docs_path, original_code_path):
    site_name = f"{original_code_path} docs"

    with open(os.path.join(original_docs_path, "index.html"), "w") as index_file:
        index_file.write(
            f"""
{generate_menu(original_docs_path,original_code_path)}
<h1>{site_name}</h1>
<h1>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</h1>
<h1>version 1.0.0</h1>
<h1>{os.path.basename((os.getcwd()))}</h1>
<div><a href="{os.path.join(original_docs_path,original_code_path,"content.html")}">content</a></div>
<div><a href="{os.path.join(original_docs_path,"indexed.html")}">alphabetic</a></div>
"""
        )


def generate_alphabetic_file(
    docs_path, names_dict, original_code_path, original_docs_path
):

    paths_dict = {
        obj: f'{p.replace(".go", ".html")}#{obj}'
        for p, objs in names_dict.items()
        for obj in objs
    }
    paths_list = sorted(paths_dict.items())

    content = (
        generate_menu(original_docs_path, original_code_path)
        + "<h3>alphabetically sorted objects</h3>"
    )

    i = 0
    for char in string.ascii_lowercase:
        content += f"<h2>{char.upper()}</h2>"
        while i < len(paths_list):
            s = paths_list[i]
            if s[0][0].lower() != char:
                i += 1
                break

            content += (
                "<pre>"
                + "<br>".join([f"<a href='{s[1].replace('/docs/','/')}'>{s[0]}</a>"])
                + "</pre>"
            )
            i += 1

    with open(os.path.join(docs_path, "indexed.html"), "w") as index_file:
        index_file.write(content)


def generate_content_files(
    curpath, source_code_structure, original_docs_path, original_code_path, names_dict
):
    content = generate_menu(original_docs_path, original_code_path)

    for name, path in source_code_structure.items():
        if isinstance(path, str):
            name = name.replace(".go", ".html")
            content += f"""<div><a href="{name}">{name}</a></div>"""
        elif isinstance(path, dict):
            content += f"""<div style="background-color:yellow">
                              <a href="{name}/content.html">{name}</a>
                           </div>
                        """
            generate_content_files(
                os.path.join(curpath, name),
                path,
                original_docs_path,
                original_code_path,
                names_dict,
            )

    os.makedirs(
        os.path.join(os.getcwd(), original_docs_path, original_code_path, curpath),
        exist_ok=True,
    )
    with open(
        os.path.join(os.getcwd(), original_code_path, curpath, "content.html"), "w"
    ) as file:
        file.write(content)
