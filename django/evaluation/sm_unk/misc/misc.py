import glob
import re
from pathlib import Path
from typing import Union, Callable, Any, List, Optional

from ruamel.yaml import YAML


def str2bool(x):
    assert x in {"True", "False", "true", "false", "null"}
    if x == "<null>":
        return None
    return x.lower() == "true"


def nullable_str(x):
    if x == "<null>":
        return None
    return x


def str2int(x):
    if x == "<null>":
        return None
    return int(x)


def filter_duplication(lst: List[Any], key_fn: Callable[[Any], Any]=None):
    key_fn = key_fn or identity_func
    keys = set()
    new_lst = []
    for item in lst:
        k = key_fn(item)
        if k in keys:
            continue
        
        keys.add(k)
        new_lst.append(item)
    return new_lst


def identity_func(x):
    return x


def get_latest_version(file_pattern: Union[str, Path]) -> int:
    """Assuming the file pattern select list of files tagged with an integer version for every run, this
    function return the latest version number that you can use to name your next run.

    For example:
    1. If your pattern matches folders: version_1, version_5, version_6, this function will return 6.
    2. If your pattern does not match anything, return 0
    """
    files = [Path(file) for file in sorted(glob.glob(str(file_pattern)))]
    if len(files) == 0:
        return 0

    file = sorted(files)[-1]
    match = re.match("[^0-9]*(\d+)[^0-9]*", file.name)
    if match is None:
        raise Exception("Invalid naming")
    return int(match.group(1))


def get_incremental_path(path: Union[str, Path]) -> str:
    path = Path(str(path))
    if path.suffix == "":
        char = "_"
    else:
        char = "."

    pattern = path.parent / f"{path.stem}{char}*{path.suffix}"
    version = get_latest_version(pattern) + 1

    return str(path.parent / f"{path.stem}{char}{version:02d}{path.suffix}")


def get_latest_path(path: Union[str, Path]) -> Optional[str]:
    path = Path(str(path))
    pattern = path.parent / f"{path.stem}.*{path.suffix}"
    version = get_latest_version(pattern)
    if version == 0:
        return None
    return str(path.parent / f"{path.stem}.{version:02d}{path.suffix}")


def auto_wrap(word: str, max_char_per_line: int, delimiters: List[str] = None, camelcase_split: bool = True) -> str:
    """
    Treat this as optimization problem, where we trying to minimize the number of line break
    but also maximize the readability in each line, i.e: maximize the number of characters in each lines

    Using greedy search.
    :param word:
    :param max_char_per_line:
    :param delimiters:
    :return:
    """
    # split original word by the delimiters
    if delimiters is None:
        delimiters = [' ', ':', '_', '/']

    sublines: List[str] = [""]
    for i, c in enumerate(word):
        if c not in delimiters:
            sublines[-1] += c

            if camelcase_split and not c.isupper() and i + 1 < len(word) and word[i + 1].isupper():
                # camelcase_split
                sublines.append("")
        else:
            sublines[-1] += c
            sublines.append("")

    new_sublines: List[str] = [""]
    for line in sublines:
        if len(new_sublines[-1]) + len(line) <= max_char_per_line:
            new_sublines[-1] += line
        else:
            new_sublines.append(line)

    return "\n".join(new_sublines)