"""Команды, изменяющие VFS в памяти: rm, chown."""

import re

from .base import CommandError, parse_options

OWNER_PATTERN = re.compile(r"^[a-z_][a-z0-9_-]*$")
SPECIAL_NAMES = (".", "..")
MIN_CHOWN_ARGS = 2


def cmd_rm(shell, args):
    """Удалить файлы и каталоги.

    ``rm [-r] [-f] [-v] путь...``: ``-r``/``-R`` — удалять каталоги
    рекурсивно, ``-f`` — не сообщать о несуществующих путях,
    ``-v`` — выводить имя каждого удалённого узла.
    """
    flags, paths = parse_options("rm", args, "rRfv")
    if not paths:
        if "f" in flags:
            return ""
        raise CommandError("rm: пропущен операнд")
    recursive = bool(flags & {"r", "R"})
    return _for_each(paths, lambda path: _remove(
        shell, path, recursive, flags
    ))


def _remove(shell, path, recursive, flags):
    """Удалить один путь; вернуть строку вывода или ``""``."""
    if path.rstrip("/").split("/")[-1] in SPECIAL_NAMES:
        raise CommandError(f"rm: отказ удалять '.' или '..': '{path}'")
    try:
        node = _resolve(shell, "rm", path)
    except CommandError:
        if "f" in flags:
            return ""
        raise
    if node.parent is None:
        raise CommandError("rm: опасно удалять корневой каталог '/'")
    if node.is_dir and not recursive:
        raise CommandError(f"rm: невозможно удалить '{path}': это каталог")
    if _is_inside(shell.cwd, node):
        shell.cwd = node.parent
    node.parent.remove(node.name)
    return f"удалён '{path}'" if "v" in flags else ""


def cmd_chown(shell, args):
    """Сменить владельца файлов и каталогов.

    ``chown [-R] [-v] владелец путь...``: ``-R`` — рекурсивно,
    ``-v`` — выводить каждое изменение.
    """
    flags, operands = parse_options("chown", args, "Rv")
    if len(operands) < MIN_CHOWN_ARGS:
        raise CommandError("chown: пропущен операнд")
    owner, paths = operands[0], operands[1:]
    if not OWNER_PATTERN.match(owner):
        raise CommandError(f"chown: недопустимый владелец '{owner}'")
    return _for_each(paths, lambda path: _change_owner(
        shell, path, owner, flags
    ))


def _change_owner(shell, path, owner, flags):
    """Сменить владельца одного пути; вернуть строку вывода."""
    node = _resolve(shell, "chown", path)
    nodes = shell.vfs.walk(node) if "R" in flags else [node]
    changes = []
    for item in nodes:
        if item.owner != owner:
            changes.append(
                f"владелец '{item.path}': {item.owner} -> {owner}"
            )
        item.owner = owner
    return "\n".join(changes) if "v" in flags else ""


def _resolve(shell, name, path):
    """Найти путь, добавив имя команды к сообщению об ошибке."""
    try:
        return shell.resolve(path)
    except CommandError as error:
        raise CommandError(f"{name}: {error}") from error


def _for_each(paths, action):
    """Применить ``action`` к каждому пути, собирая вывод и ошибки.

    Ошибка одного пути не мешает обработать остальные; в конце все
    ошибки возбуждаются одним :class:`CommandError`.
    """
    outputs, errors = [], []
    for path in paths:
        try:
            outputs.append(action(path))
        except CommandError as error:
            errors.append(str(error))
    output = "\n".join(filter(None, outputs))
    if errors:
        raise CommandError("\n".join(errors), partial=output)
    return output


def _is_inside(node, ancestor):
    """Проверить, лежит ли ``node`` в поддереве ``ancestor``."""
    while node is not None:
        if node is ancestor:
            return True
        node = node.parent
    return False
