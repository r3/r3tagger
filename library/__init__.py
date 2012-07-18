import os


def extension(path):
    return os.path.splitext(path)[-1]


def parent(path, levels=1):
    # I know, recursion, but this is Python
    if path.endswith(os.path.sep):
        result = os.path.dirname(path)
    else:
        result = path

    for level in range(levels):
        result = os.path.dirname(result)

    return result


def filename(path):
    return os.path.split(path)[-1]
