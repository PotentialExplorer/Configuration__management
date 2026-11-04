"""Команды навигации по VFS: ls, cd, tree."""

from .base import CommandError, parse_options, require_dir

MAX_CD_ARGS = 1
MAX_TREE_ARGS = 1
SINGLE_PATH = 1
DIR_MODE = "drwxr-xr-x"
FILE_MODE = "-rw-r--r--"
DIR_SIZE = 4096
OWNER_WIDTH = 8
SIZE_WIDTH = 6
BRANCH = "├── "
LAST_BRANCH = "└── "
PIPE = "│   "
SPACE = "    "


def cmd_ls(shell, args):
    """Вывести содержимое каталогов.

    ``ls [-l] [-a] [путь...]``: ``-l`` — подробный формат,
    ``-a`` — показывать ``.`` и ``..``.
    """
    flags, paths = parse_options("ls", args, "la")
    paths = paths or ["."]
    nodes = [shell.resolve(path) for path in paths]
    blocks = []
    for path, node in zip(paths, nodes):
        listing = _list_node(node, flags)
        if len(nodes) > SINGLE_PATH and node.is_dir:
            listing = f"{path}:\n{listing}".rstrip("\n")
        blocks.append(listing)
    return "\n\n".join(blocks)


def _list_node(node, flags):
    """Сформировать вывод ``ls`` для одного узла."""
    if not node.is_dir:
        entries = [(node.name, node)]
    else:
        entries = [(child.name, child) for child in node.sorted_children()]
        if "a" in flags:
            parent = node.parent or node
            entries = [(".", node), ("..", parent)] + entries
    if "l" in flags:
        return "\n".join(_long_line(name, item) for name, item in entries)
    return "  ".join(name for name, _ in entries)


def _long_line(name, node):
    """Строка подробного формата ``ls -l``."""
    mode = DIR_MODE if node.is_dir else FILE_MODE
    size = DIR_SIZE if node.is_dir else node.size
    return (
        f"{mode} {node.owner:<{OWNER_WIDTH}} {size:>{SIZE_WIDTH}} {name}"
    )


def cmd_cd(shell, args):
    """Сменить текущий каталог: ``cd [путь]`` (без аргумента — домой)."""
    if len(args) > MAX_CD_ARGS:
        raise CommandError("cd: слишком много аргументов")
    target = shell.resolve(args[0] if args else "~")
    shell.cwd = require_dir("cd", target)
    return ""


def cmd_tree(shell, args):
    """Вывести дерево каталогов: ``tree [-d] [путь]``.

    ``-d`` — показывать только каталоги.
    """
    flags, paths = parse_options("tree", args, "d")
    if len(paths) > MAX_TREE_ARGS:
        raise CommandError("tree: слишком много аргументов")
    root = require_dir("tree", shell.resolve(paths[0] if paths else "."))
    lines = [paths[0] if paths else "."]
    counts = {"dirs": 0, "files": 0}
    _tree_lines(root, "", "d" in flags, lines, counts)
    lines.append("")
    lines.append(f"каталогов: {counts['dirs']}, файлов: {counts['files']}")
    return "\n".join(lines)


def _tree_lines(node, prefix, dirs_only, lines, counts):
    """Рекурсивно добавить в ``lines`` строки поддерева ``node``."""
    children = node.sorted_children()
    if dirs_only:
        children = [child for child in children if child.is_dir]
    for index, child in enumerate(children):
        last = index == len(children) - 1
        lines.append(prefix + (LAST_BRANCH if last else BRANCH) + child.name)
        if child.is_dir:
            counts["dirs"] += 1
            extension = SPACE if last else PIPE
            _tree_lines(child, prefix + extension, dirs_only, lines, counts)
        else:
            counts["files"] += 1
