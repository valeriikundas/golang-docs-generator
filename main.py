import os
import re
import shutil
import string
import webbrowser
from parser import Parser, build_mkdocs_files

from builders import (
    build_file_structure,
    build_mkdocs_structure_string,
    get_cleaned_from_empty_children,
)
from utils import (
    get_lines_above_that_start_with_comment_sign,
    get_lines_below_that_start_with_sign,
    mark_code,
)

path = "redis"

docs_path = "docs"
site_name = "Golang Docs"

if os.path.exists("docs"):
    shutil.rmtree("docs")

source_code_structure = build_file_structure(path)
source_code_structure = get_cleaned_from_empty_children(source_code_structure)

mkdocs_config_file_content = build_mkdocs_structure_string(source_code_structure, tab=2)
with open("mkdocs.yml", "w") as config_file:
    config_file.write(
        f"site_name: {site_name}\nnav:\n  - Home: index.md\n{mkdocs_config_file_content}"
    )


build_mkdocs_files(source_code_structure, doc_path=f"docs/{path}")

webbrowser.open("http://localhost:8000", new=2)
os.system("mkdocs serve")
