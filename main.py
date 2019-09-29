import os
import string
import re

path = "go-master"

f = "src/database/sql/sql.go"
file = os.path.join(path, f)
source_code = open(file).readlines()

docs_path = "docs"
site_name = "Golang Docs"

with open("mkdocs.yml", "w") as config_file:
    folder_str = ""
    os.chdir(path)
    os.makedirs(os.path.dirname(f), exist_ok=True)

    objs = f.split("/")
    objs[-1] = objs[-1].split(".")[0]
    tab_size = 0
    for i, obj in enumerate(objs):
        if i == len(objs) - 1:
            tab_size += 2
            folder_str += " " * tab_size + f"- {obj}: {'/'.join(objs[:i+1])+'.md'}\n"
        else:
            tab_size += 2
            folder_str += " " * tab_size + f"- {obj}:\n"
            os.chdir(obj)
        # os.chdir("..")

    config_file.write(
        f"site_name: {site_name}\n" + "nav:\n" + "  - Home: index.md\n" + folder_str
    )
# nav:
#     - Home: index.md
#     - src:
#         - database:
#             - sql:
#                 - driver:
#                     - driver: src/database/sql/driver/driver.md
#                 - sql: src/database/sql/sql.md


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
class_method_pattern = r""  # TODO:
class_pattern = r"type .+ struct {"


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
        if source_code[j].startswith(")"):
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

for i, line in enumerate(source_code):
    # multiple constants
    match = re.match(constant_multiple_pattern, line)
    if match:
        print(i, "multiple constant ")

        doc = (
            get_lines_above_that_start_with_comment_sign(source_code, i)
            + source_code[i]
            + get_lines_below_that_start_with_sign(source_code, i, ")")
        )
        constants_documentation.append(mark_code(doc))

    # single constant
    match = re.match(constant_single_pattern, line)
    if match:
        print(i, "single constant")
        doc = (
            get_lines_above_that_start_with_comment_sign(source_code, i)
            + source_code[i]
        )
        constants_documentation.append(mark_code(doc))

    # single variable
    match = re.match(variable_single_pattern, line)
    if match:
        print(i, "single variable")
        doc = (
            get_lines_above_that_start_with_comment_sign(source_code, i)
            + source_code[i]
        )
        variable_documentation.append(mark_code(doc))

    # TODO: multiple variable
    match = re.match(variable_multiple_pattern, line)
    if match:
        print(i, "multiple variable")
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
        print(i, "function")
        doc = get_lines_above_that_start_with_comment_sign(
            source_code, i
        ) + source_code[i].replace("{", "")
        functions_documentation.append(mark_code(doc))

    # type_match = re.match(type_pattern, line)


with open(doc_file, "w") as doc_file:
    doc_file.write(file_documentation)
    doc_file.write("## Constants\n")
    doc_file.write("".join(constants_documentation))
    doc_file.write("## Variables\n")
    doc_file.write("".join(variable_documentation))
    doc_file.write("## Functions\n")
    doc_file.write("".join(functions_documentation))
