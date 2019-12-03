import os
from parser import Parser


def build_file_structure(path):
    objects = os.listdir(path)
    file_structure = dict()
    for obj in objects:
        j = os.path.join(path, obj)
        if os.path.isdir(j):
            if obj == ".git":  # skip git folder
                continue
            file_structure[obj] = build_file_structure(j)
        elif os.path.isfile(os.path.abspath(j)) and obj.endswith(".go"):
            if obj.endswith("_test.go"):  # skip test files
                continue
            file_structure[obj] = j
    return file_structure


def build_doc_files(source_code_structure_or_filename, names_dict, doc_path):
    if not os.path.exists(doc_path) and not doc_path.endswith(".go"):
        os.makedirs(doc_path, exist_ok=True)

    if isinstance(source_code_structure_or_filename, str):
        filepath = source_code_structure_or_filename
        doc_filepath = os.path.join("docs", filepath).replace(".go", ".html")
        code = open(filepath, "r").readlines()

        documentation = Parser(code)
        documentation.process()
        documentation.write(doc_filepath)

        names_dict[doc_path] = list(documentation.class_methods.keys())

        return

    for dirname, nested in list(source_code_structure_or_filename.items()):
        build_doc_files(nested, names_dict, os.path.join(doc_path, dirname))
