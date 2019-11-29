# TODO:

# — Змiст, який складається з роздiлiв, що вiдповiдають рiвню пiдкаталогiв вхiдного
# каталогу з програмними кодами. Кожен роздiл має мiстити власний змiст, кожен
# елемент якого вказує на документацiю певного пiдкаталогу або файлу.

# — Алфавiтний покажчик, який має мiстити посилання на описи усiх iмен з усiх каталогiв та файлiв.

# classes and methods that belong to them

import datetime
import os
import re
import shutil
import string
import webbrowser

import click

from builders import (
    build_doc_files,
    build_file_structure,
    generate_content_files,
    get_cleaned_from_empty_children,
)
from utils import (
    generate_index_file,
    get_lines_above_that_start_with_comment_sign,
    get_lines_below_that_start_with_sign,
    mark_code,
)


@click.command()
@click.option("--path", help="code folder path")
@click.option("--output", help="output docs path", default="docs")
def entrypoint(path, output):
    code_path = path
    docs_path = output

    if os.path.exists(docs_path):
        shutil.rmtree(docs_path)
    os.makedirs(docs_path)

    source_code_structure = build_file_structure(code_path)
    # source_code_structure = get_cleaned_from_empty_children(source_code_structure)

    names_dict = dict()
    build_doc_files(
        source_code_structure, names_dict, doc_path=f"{docs_path}/{code_path}"
    )

    generate_content_files("", source_code_structure, docs_path, code_path, names_dict)
    generate_index_file(docs_path, code_path, source_code_structure)

    # os.system(f"google-chrome {os.path.join(os.getcwd(),'docs/index.html')}")


if __name__ == "__main__":
    entrypoint()
