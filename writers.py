import datetime
import os


def generate_index_file(docs_path, path):
    site_name = f"{path} docs"
    with open(os.path.join(docs_path, "index.html"), "w") as index_file:
        index_file.write(
            f"""
<h1>{site_name}</h1>
<h1>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</h1>
<h1>version 1.0.0</h1>
<h1>{os.path.basename((os.getcwd()))}</h1>
<div><a href="{os.path.join(docs_path,path,"content.html")}">content</a></div>
<div><a href="{os.path.join(docs_path,"indexed.html")}">alphabetic</a></div>
"""
        )


def generate_indexed_file(docs_path, names_dict):
    paths_dict = {
        obj: f'{p.replace(".go", ".html")}#{obj}'
        for p, objs in names_dict.items()
        for obj in objs
    }
    paths_list = sorted(paths_dict.items())

    content = "<h3>alphabetically sorted objects</h3>"
    content += (
        "<pre>"
        + "<br>".join([f"<a href='{i[1][5:]}'>{i[0]}</a>" for i in paths_list])
        + "</pre>"
    )

    with open(os.path.join(docs_path, "indexed.html"), "w") as index_file:
        index_file.write(content)


def generate_content_files(
    curpath, source_code_structure, docs_path, code_path, names_dict
):
    content = ""
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
                os.path.join(curpath, name), path, docs_path, code_path, names_dict
            )

    os.makedirs(os.path.join(os.getcwd(), docs_path, code_path, curpath), exist_ok=True)
    with open(
        os.path.join(os.getcwd(), docs_path, code_path, curpath, "content.html"), "w"
    ) as file:
        file.write(content)
