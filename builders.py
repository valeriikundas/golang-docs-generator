import os


def build_file_structure(path):
    objects = os.listdir(path)
    d = dict()
    for obj in objects:
        j = os.path.join(path, obj)
        if os.path.isdir(j):
            d[obj] = build_file_structure(j)
        elif os.path.isfile(os.path.abspath(j)) and obj.endswith(".go"):
            d[obj] = j
    return d


# FIXME:does not work
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
    # for k in structure.keys():
    #     if is_empty(structure[k]):
    #         del structure[k]
    #         # TODO:will it work?


def is_empty(d):
    if type(d) is str:
        return False

    if not len(d):
        return True

    for k in d:
        if not is_empty(d[k]):
            return False


def build_mkdocs_structure_string(d, tab=0, indent=4):
    s = ""
    for key in d:
        if type(d[key]) is str:
            s += (
                " " * tab
                + f"- {d[key].split('/')[-1].replace('.go','')}: {d[key].replace('.go','.md')}\n"
            )
        else:
            s += " " * tab + f"- {key}:\n"
            s += build_mkdocs_structure_string(d[key], tab + indent)
    return s
