import os
import string
import re

path = "go-master"

docs_path = "docs"
site_name = "Golang Docs"


def build_source_code_structure(path):
    objects = os.listdir(path)
    d = dict()
    for obj in objects:
        j = os.path.join(path, obj)
        if os.path.isdir(j):
            d[obj] = build_source_code_structure(j)
        elif os.path.isfile(os.path.abspath(j)) and obj.endswith(".go"):
            d[obj] = j
    return d


# folders_structure = build(path)
source_code_structure = {
    "src": {
        "database": {
            "sql": {
                "sql.go": "src/database/sql/sql.go",
                "driver": {"driver.go": "src/database/sql/driver/driver.go"},
            }
        }
    }
}


def build_mkdocs_structure(d, tab=0):
    s = ""
    for key in d:
        if type(d[key]) is str:
            s += (
                " " * tab
                + f"- {d[key].split('/')[-1].replace('.go','')}: {d[key].replace('.go','.md')}\n"
            )
        else:
            s += " " * tab + f"- {key}:\n"
            s += build_mkdocs_structure(d[key], tab + 2)
    return s


s = build_mkdocs_structure(source_code_structure, 2)

with open("mkdocs.yml", "w") as config_file:
    config_file.write(
        f"site_name: {site_name}\n" + "nav:\n" + "  - Home: index.md\n" + s
    )

f = "src/database/sql/sql.go"
file = os.path.join(path, f)
source_code = open(file).readlines()


doc_file_dir_path = os.path.join(docs_path, os.path.dirname(f))

os.makedirs(doc_file_dir_path, exist_ok=True)

doc_file = os.path.join(doc_file_dir_path, os.path.basename(f).replace(".go", ".md"))

url_pattern = r"https?://[a-z.]+\/[a-z/]+"
constant_single_pattern = r"const .+=.+"
constant_multiple_pattern = r"const \("
variable_single_pattern = r"var .+=.+"
variable_multiple_pattern = r"var \("
function_pattern = (
    r"func [A-Za-z_]+\(.*\).* {"
)  # if you want only exported methods, insert [A-Z] after func
class_method_pattern = r"func \(.+ \*?([a-zA-Z]+)\) [A-Za-z_]+\(.*\).*"
type_pattern = r"type .+ {?"


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
    return "```go\n" + s + "```\n"


file_documentation = ""
for line in source_code:
    if line.startswith("//") or len(line.split()) == 0:
        file_documentation += line[2:]
    else:
        break

urls = re.findall(url_pattern, file_documentation)
for i in urls:
    file_documentation = file_documentation.replace(i, f"<{i}>")

# TODO:to list. join in the end
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

    # TODO: multiple variable
    match = re.match(variable_multiple_pattern, line)
    if match:
        doc = (
            get_lines_above_that_start_with_comment_sign(source_code, i)
            + source_code[i]
            + get_lines_below_that_start_with_sign(source_code, i, ")")
        )
        variable_documentation.append(mark_code(doc))

    # TODO: functions
    # TODO: classes

    match = re.match(function_pattern, line)
    if match:
        doc = get_lines_above_that_start_with_comment_sign(
            source_code, i
        ) + source_code[i].replace("{", "")
        functions_documentation.append(mark_code(doc))

    match = re.match(type_pattern, line)
    if match:
        print(i, match)
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

    match = re.match(class_method_pattern, line)
    if match:
        print(i, match)
        class_ = match.groups()[0]

        if class_ in class_methods:
            class_methods[class_].append(match.string)
        else:
            class_methods[class_] = [match.string]

        doc = (
            get_lines_above_that_start_with_comment_sign(source_code, i)
            + source_code[i]
        )
        methods_documentation.append(mark_code(doc))

with open(doc_file, "w") as doc_file:
    doc_file.write(file_documentation)
    doc_file.write("## Constants\n")
    doc_file.write("".join(constants_documentation))
    doc_file.write("## Variables\n")
    doc_file.write("".join(variable_documentation))
    doc_file.write("## Functions\n")
    doc_file.write("".join(functions_documentation))
    doc_file.write("## Classes\n")
    doc_file.write("".join(classes_documentation))
    doc_file.write("## Methods\n")
    doc_file.write("".join(methods_documentation))
