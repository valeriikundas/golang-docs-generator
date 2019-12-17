import re

from utils import (
    get_lines_above_that_start_with_comment_sign,
    get_lines_below_that_start_with_sign,
    mark_code,
)
from writers import generate_menu

URL_PATTERN = r"https?://[a-z.]+\/[a-z/]+"
CONSTANT_SINGLE_PATTERN = r"const .+=.+"
CONSTANT_MULTIPLE_PATTERN = r"const \("
VARIABLE_SINGLE_PATTERN = r"var .+=.+"
VARIABLE_MULTIPLE_PATTERN = r"var \("
# for only Exported methods change to [A-Z] after func
FUNCTION_PATTERN = r"func [A-Za-z_]+\(.*\).* {"
CLASS_METHOD_PATTERN = r"func \(.+ \*?([a-zA-Z]+)\) [A-Za-z_]+\(.*\).*"
TYPE_PATTERN = r"type .+"


class Parser:
    def __init__(self, source_code, original_docs_path, original_code_path):
        self.original_docs_path = original_docs_path
        self.original_code_path = original_code_path
        self.source_code = source_code
        self.file_documentation = ""
        self.imports_documentation = ""
        self.constants_documentation = list()
        self.variable_documentation = list()
        self.classes_documentation = list()
        self.functions_documentation = list()
        self.methods_documentation = list()
        self.class_methods = dict()

    def process(self):
        self.process_file_documentation()
        self.process_urls_in_file_description()
        self.process_imports()

        for i, line in enumerate(self.source_code):

            self.process_multiple_constants(line, i)
            self.process_variable_single(line, i)
            self.process_variables_multiple(line, i)
            self.process_functions(line, i)
            self.process_types(line, i)
            self.process_class_methods(line, i)

    def process_imports(self,):
        imports = ""
        for i, val in enumerate(self.source_code):
            if val.startswith("import"):
                imports += val
                i += 1
                if val.find("(") != -1:
                    while i < len(self.source_code):
                        imports += self.source_code[i]

                        if self.source_code[i].find(")") != -1:
                            break
                        i += 1

        self.imports_documentation += imports

    def process_file_documentation(self):
        for line in self.source_code:
            if line.startswith("//") or not line.split():
                self.file_documentation += line[2:]
            else:
                break

    def process_urls_in_file_description(self):
        urls = re.findall(URL_PATTERN, self.file_documentation)
        for url in urls:
            self.file_documentation = self.file_documentation.replace(
                url, f'<a href="{url}">i<a>'
            )

    def process_multiple_constants(self, line, index):
        match = re.match(CONSTANT_MULTIPLE_PATTERN, line)
        if match:
            doc = (
                get_lines_above_that_start_with_comment_sign(self.source_code, index)
                + self.source_code[index]
                + get_lines_below_that_start_with_sign(self.source_code, index, ")")
            )
            self.constants_documentation.append(mark_code(doc))

    def process_constant_single(self, line, index):
        match = re.match(CONSTANT_SINGLE_PATTERN, line)
        if match:
            doc = (
                get_lines_above_that_start_with_comment_sign(self.source_code, index)
                + self.source_code[index]
            )
            self.constants_documentation.append(mark_code(doc))

    def process_variable_single(self, line, index):
        match = re.match(VARIABLE_SINGLE_PATTERN, line)
        if match:
            doc = (
                get_lines_above_that_start_with_comment_sign(self.source_code, index)
                + self.source_code[index]
            )
            self.variable_documentation.append(mark_code(doc))

    def process_variables_multiple(self, line, index):
        match = re.match(VARIABLE_MULTIPLE_PATTERN, line)
        if match:
            doc = (
                get_lines_above_that_start_with_comment_sign(self.source_code, index)
                + self.source_code[index]
                + get_lines_below_that_start_with_sign(self.source_code, index, ")")
            )
            self.variable_documentation.append(mark_code(doc))

    def process_functions(self, line, index):
        match = re.match(FUNCTION_PATTERN, line)
        if match:
            doc = get_lines_above_that_start_with_comment_sign(self.source_code, index)
            if (
                get_lines_above_that_start_with_comment_sign(self.source_code, index)
                == ""
            ):
                doc = "//<span style='background-color:yellow'>EMPTY FUNCTION DOCUMENTATION</span>\n"
            doc += self.source_code[index].replace("{", "")
            self.functions_documentation.append(mark_code(doc))

    def process_types(self, line, index):
        match = re.match(TYPE_PATTERN, line)
        if match:
            doc = (
                get_lines_above_that_start_with_comment_sign(self.source_code, index)
                + self.source_code[index]
                + (
                    get_lines_below_that_start_with_sign(self.source_code, index, "}")
                    if match[0][-1] == "{"
                    else ""
                )
            )
            self.classes_documentation.append(mark_code(doc))

            class_name = re.match(r"type (\w+) ", line)
            if class_name:
                class_name = class_name.group(1)
                if class_name in self.class_methods:
                    self.class_methods[class_name].append(doc)
                else:
                    self.class_methods[class_name] = [doc]

    def process_class_methods(self, line, index):
        match = re.match(CLASS_METHOD_PATTERN, line)
        if match:
            class_ = match.groups()[0]

            match_string = match.string
            pos = match_string.find("{")
            if pos != -1:
                match_string = match_string[:pos]

            if class_ in self.class_methods:
                self.class_methods[class_].append(match_string)
            else:
                self.class_methods[class_] = [match_string]

            doc = get_lines_above_that_start_with_comment_sign(
                self.source_code, index
            ) + self.source_code[index].replace("{", "")
            self.methods_documentation.append(mark_code(doc))

    def write(self, doc_filepath):
        with open(doc_filepath, "w") as doc_file:
            doc_file.write(
                generate_menu(self.original_docs_path, self.original_code_path)
            )
            doc_file.write(f"<pre><code>{self.imports_documentation}</code></pre>")
            doc_file.write(f"<pre><code>{self.file_documentation}</code></pre>")
            doc_file.write("<h3>Constants</h3>")
            doc_file.write("".join(self.constants_documentation))
            doc_file.write("<h3>Variables</h3>")
            doc_file.write("".join(self.variable_documentation))
            doc_file.write("<h3>Functions</h3>")
            doc_file.write("".join(self.functions_documentation))
            doc_file.write("<h3>Classes</h3>")

            methods_content = []
            for class_name, class_methods in self.class_methods.items():
                methods_content.append(f"<h4 id='{class_name}'>{class_name}</h4>")
                methods_content.append(f"{class_methods[0]}")
                methods_content.append("".join(class_methods[1:]))

            doc_file.write("<pre><code>" + "\n".join(methods_content) + "</code></pre>")
