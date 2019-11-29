import json
import os
import re

from utils import (
    get_lines_above_that_start_with_comment_sign,
    get_lines_below_that_start_with_sign,
    mark_code,
)

url_pattern = r"https?://[a-z.]+\/[a-z/]+"
constant_single_pattern = r"const .+=.+"
constant_multiple_pattern = r"const \("
variable_single_pattern = r"var .+=.+"
variable_multiple_pattern = r"var \("
function_pattern = r"func [A-Za-z_]+\(.*\).* {"  # if you want only exported methods, insert [A-Z] after func
class_method_pattern = r"func \(.+ \*?([a-zA-Z]+)\) [A-Za-z_]+\(.*\).*"
type_pattern = r"type .+"


class Parser:
    def __init__(self, names_dict, url):
        self.names_dict = names_dict
        self.file_documentation = ""
        self.constants_documentation = list()
        self.variable_documentation = list()
        self.classes_documentation = list()
        self.functions_documentation = list()
        self.methods_documentation = list()
        self.class_methods = dict()
        self.parent_url = "/".join(url.split("/")[:-1])

    def do(self, source_code):

        file_documentation = ""
        for line in source_code:
            if line.startswith("//") or len(line.split()) == 0:
                file_documentation += line[2:]
            else:
                break

        urls = re.findall(url_pattern, file_documentation)
        for i in urls:
            file_documentation = file_documentation.replace(i, f'<a href="{i}">i<a>')

        constants_documentation = list()
        variable_documentation = list()
        classes_documentation = list()
        functions_documentation = list()
        methods_documentation = list()
        class_methods = dict()

        for i, line in enumerate(source_code):
            # multiple constants
            match = re.match(constant_multiple_pattern, line)
            if match:
                doc = (
                    get_lines_above_that_start_with_comment_sign(source_code, i)
                    + source_code[i]
                    + get_lines_below_that_start_with_sign(source_code, i, ")")
                )
                constants_documentation.append(mark_code(doc))

            # single constant
            match = re.match(constant_single_pattern, line)
            if match:
                doc = (
                    get_lines_above_that_start_with_comment_sign(source_code, i)
                    + source_code[i]
                )
                constants_documentation.append(mark_code(doc))

            # single variable
            match = re.match(variable_single_pattern, line)
            if match:
                doc = (
                    get_lines_above_that_start_with_comment_sign(source_code, i)
                    + source_code[i]
                )
                variable_documentation.append(mark_code(doc))

            match = re.match(variable_multiple_pattern, line)
            if match:
                doc = (
                    get_lines_above_that_start_with_comment_sign(source_code, i)
                    + source_code[i]
                    + get_lines_below_that_start_with_sign(source_code, i, ")")
                )
                variable_documentation.append(mark_code(doc))

            match = re.match(function_pattern, line)
            if match:
                doc = get_lines_above_that_start_with_comment_sign(
                    source_code, i
                ) + source_code[i].replace("{", "")
                functions_documentation.append(mark_code(doc))

            match = re.match(type_pattern, line)
            if match:
                doc = (
                    get_lines_above_that_start_with_comment_sign(source_code, i)
                    + source_code[i]
                    + (
                        get_lines_below_that_start_with_sign(source_code, i, "}")
                        if match[0][-1] == "{"
                        else ""
                    )
                )
                classes_documentation.append(mark_code(doc))

                class_name = re.match("type (\w+) ", line)
                if class_name:
                    class_name = class_name.group(1)
                    if class_name in class_methods:
                        class_methods[class_name].append(doc)
                    else:
                        class_methods[class_name] = [doc]

            match = re.match(class_method_pattern, line)
            if match:
                class_ = match.groups()[0]

                match_string = match.string
                pos = match_string.find("{")
                if pos != -1:
                    match_string = match_string[:pos]

                if class_ in class_methods:
                    class_methods[class_].append(match_string)
                else:
                    class_methods[class_] = [match_string]

                doc = get_lines_above_that_start_with_comment_sign(
                    source_code, i
                ) + source_code[i].replace("{", "")
                methods_documentation.append(mark_code(doc))

        self.file_documentation = file_documentation
        self.constants_documentation = constants_documentation
        self.variable_documentation = variable_documentation
        self.classes_documentation = classes_documentation
        self.functions_documentation = functions_documentation
        self.methods_documentation = methods_documentation
        self.class_methods = class_methods

    def write(self, doc_file):
        with open(doc_file, "w") as doc_file:
            doc_file.write(f'<a href="content.html">back</a><br>')
            doc_file.write(f"<pre><code>{self.file_documentation}</code></pre>")
            doc_file.write("<h3>Constants</h3>")
            doc_file.write("".join(self.constants_documentation))
            doc_file.write("<h3>Variables</h3>")
            doc_file.write("".join(self.variable_documentation))
            doc_file.write("<h3>Functions</h3>")
            doc_file.write("".join(self.functions_documentation))
            # doc_file.write("<h3>Classes</h3>")
            # doc_file.write("".join(self.classes_documentation))
            # doc_file.write("<h3>Methods</h3>")
            # doc_file.write("".join(self.methods_documentation))
            doc_file.write("<h3>Classes</h3>")

            methods_content = []
            for class_name, class_methods in self.class_methods.items():
                methods_content.append(f"<h4 id='{class_name}'>{class_name}</h4>")
                methods_content.append(f"{class_methods[0]}")
                methods_content.append("".join(class_methods[1:]))

            doc_file.write(
                "<pre><code>" + "\n".join(methods_content) + "</code></pre><br>"
            )


def build_file_structure(path):
    objects = os.listdir(path)
    d = dict()
    for obj in objects:
        j = os.path.join(path, obj)
        if os.path.isdir(j):
            if obj == ".git":  # skip git folder
                continue
            d[obj] = build_file_structure(j)
        elif os.path.isfile(os.path.abspath(j)) and obj.endswith(".go"):
            if obj.endswith("_test.go"):  # skip test files
                continue
            d[obj] = j
    return d


def get_cleaned_from_empty_children(structure):
    # squared recursion not too speedy for big file docs
    if type(structure) is str:
        return structure

    if type(structure) is dict and not len(structure):
        return False

    return {
        k: get_cleaned_from_empty_children(v)
        for k, v in structure.items()
        if not is_empty(v)
    }


def is_empty(d):
    if type(d) is str:
        return False

    if not len(d):
        return True

    for k in d:
        if not is_empty(d[k]):
            return False


def generate_content_files(
    curpath, source_code_structure, docs_path, code_path, names_dict
):
    content = ""
    for name, path in source_code_structure.items():
        if type(path) is str:
            name = name.replace(".go", ".html")
            # path = path.replace(".go", ".html")
            content += f"""<div><a href="{name}">{name}</a></div>"""
        elif type(path) is dict:
            content += f"""<div style="background-color:yellow"><a href="{name}/content.html">{name}</a></div>"""
            generate_content_files(
                os.path.join(curpath, name), path, docs_path, code_path, names_dict,
            )

    content += "<br><br>"
    content += f"<b>{curpath}</b>"
    content += (
        "<pre>"
        + "<br>".join(
            [
                "<br>".join(
                    [
                        f"<a href='{i.replace('.go','.html')}#{j}'>{j}</a>"
                        for j in names_dict[i]
                    ]
                )
                for i in names_dict
                if i.find(curpath) != -1
            ]
        )
        + "</pre>"
    )

    os.makedirs(os.path.join(os.getcwd(), docs_path, code_path, curpath), exist_ok=True)
    with open(
        os.path.join(os.getcwd(), docs_path, code_path, curpath, "content.html"), "w"
    ) as file:
        file.write(content)


def build_doc_files(
    source_code_structure_or_filename_bad_name_for_variable, names_dict, doc_path,
):
    if not os.path.exists(doc_path) and not doc_path.endswith(".go"):
        os.makedirs(doc_path, exist_ok=True)

    if type(source_code_structure_or_filename_bad_name_for_variable) is str:

        filepath = source_code_structure_or_filename_bad_name_for_variable
        doc_filepath = os.path.join("docs", filepath).replace(".go", ".html")
        code = open(filepath, "r").readlines()

        documentation = Parser(
            names_dict, source_code_structure_or_filename_bad_name_for_variable
        )
        documentation.do(code)
        documentation.write(doc_filepath)

        names_dict[doc_path.split("/")[-1]] = list(documentation.class_methods.keys())

        return

    for dirname, nested in list(
        source_code_structure_or_filename_bad_name_for_variable.items()
    ):
        build_doc_files(nested, names_dict, os.path.join(doc_path, dirname))
