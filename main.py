import os
import shutil

import click

from builders import build_doc_files, build_file_structure
from writers import generate_content_files, generate_index_file, generate_indexed_file


@click.command()
@click.option("--path", help="code folder path")
@click.option("--output", help="output docs path", default="docs")
def entrypoint(path, output):
    code_path = os.path.abspath(path)
    docs_path = os.path.abspath(output)

    if os.path.exists(docs_path):
        shutil.rmtree(docs_path)
    os.makedirs(docs_path)

    source_code_structure = build_file_structure(code_path)

    names_dict = dict()
    build_doc_files(source_code_structure, names_dict, f"{docs_path}/{code_path}")

    generate_content_files("", source_code_structure, docs_path, code_path, names_dict)
    generate_indexed_file(docs_path, names_dict)
    generate_index_file(docs_path, code_path)

    # os.system(f"google-chrome {os.path.join(os.getcwd(),'docs/index.html')}")


if __name__ == "__main__":
    entrypoint()
