import os
import re

from builders import build_file_structure, build_mkdocs_structure_string
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
type_pattern = r"type .+ {?"


class Parser:
    def __init__(self):
        self.file_documentation = ""
        self.constants_documentation = list()
        self.variable_documentation = list()
        self.classes_documentation = list()
        self.functions_documentation = list()
        self.methods_documentation = list()
        self.class_methods = dict()

    def do(self, source_code):

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

        self.file_documentation = file_documentation
        self.constants_documentation = constants_documentation
        self.variable_documentation = variable_documentation
        self.classes_documentation = classes_documentation
        self.functions_documentation = functions_documentation
        self.methods_documentation = methods_documentation
        self.class_methods = class_methods

    def write(self, doc_file):
        with open(doc_file, "w") as doc_file:
            doc_file.write(self.file_documentation)
            doc_file.write("## Constants\n")
            doc_file.write("".join(self.constants_documentation))
            doc_file.write("## Variables\n")
            doc_file.write("".join(self.variable_documentation))
            doc_file.write("## Functions\n")
            doc_file.write("".join(self.functions_documentation))
            doc_file.write("## Classes\n")
            doc_file.write("".join(self.classes_documentation))
            doc_file.write("## Methods\n")
            doc_file.write("".join(self.methods_documentation))


def build_mkdocs_files(
    source_code_structure_or_filename_bad_name_for_variable, doc_path
):
    print(doc_path)
    if not os.path.exists(doc_path) and not doc_path.endswith(".go"):
        os.makedirs(doc_path, exist_ok=True)

    if type(source_code_structure_or_filename_bad_name_for_variable) is str:
        filepath = source_code_structure_or_filename_bad_name_for_variable
        doc_filepath = os.path.join("docs", filepath).replace(".go", ".md")
        code = open(filepath, "r").readlines()

        documentation = Parser()
        documentation.do(code)
        documentation.write(doc_filepath)

        return

    for dirname, nested in list(
        source_code_structure_or_filename_bad_name_for_variable.items()
    ):
        build_mkdocs_files(nested, os.path.join(doc_path, dirname))
