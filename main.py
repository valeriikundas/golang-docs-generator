import os
import shutil

import click

from builders import build_doc_files, build_file_structure
from writers import (
    generate_content_files,
    generate_index_file,
    generate_alphabetic_file,
)

original_code_path = ""
original_docs_path = ""


@click.command()
@click.option("--path", help="code folder path")
@click.option("--output", help="output docs path", default="docs")
def entrypoint(path, output):
    global original_code_path
    original_code_path = os.path.abspath(path)
    global original_docs_path
    original_docs_path = os.path.abspath(output)

    if os.path.exists(original_docs_path):
        shutil.rmtree(original_docs_path)
    os.makedirs(original_docs_path)

    source_code_structure = build_file_structure(original_code_path)

    names_dict = dict()
    build_doc_files(
        source_code_structure,
        names_dict,
        f"{original_docs_path}/{path}",
        original_docs_path,
        original_code_path,
    )

    generate_content_files(
        f"{path}",
        source_code_structure,
        original_docs_path,
        original_code_path,  # path it was
        names_dict,
    )
    generate_alphabetic_file(
        original_docs_path, names_dict, original_code_path, original_docs_path
    )
    generate_index_file(original_docs_path, original_code_path)

    # os.system(f"google-chrome {os.path.join(os.getcwd(),'docs/index.html')}")


if __name__ == "__main__":
    entrypoint()
