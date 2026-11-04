"""Общие средства для реализации команд."""

OPTION_PREFIX = "-"
END_OF_OPTIONS = "--"


class CommandError(Exception):
    """Ошибка выполнения команды (неверные аргументы и т. п.).

    :ivar partial: вывод той части работы, что успела выполниться.
    """

    def __init__(self, message, partial=""):
        """Создать ошибку с сообщением и частичным выводом."""
        super().__init__(message)
        self.partial = partial


def parse_options(name, args, allowed):
    """Отделить ключи вида ``-l``, ``-rf`` от операндов.

    Разбор ключей заканчивается на ``--`` или первом операнде.

    :param name: имя команды (для сообщений об ошибках).
    :param args: аргументы команды.
    :param allowed: строка допустимых однобуквенных ключей.
    :return: кортеж ``(множество_ключей, операнды)``.
    :raises CommandError: при неизвестном ключе.
    """
    flags = set()
    rest = list(args)
    while rest and _is_option(rest[0]):
        arg = rest.pop(0)
        if arg == END_OF_OPTIONS:
            break
        for flag in arg[1:]:
            if flag not in allowed:
                raise CommandError(f"{name}: неверный ключ -- '{flag}'")
            flags.add(flag)
    return flags, rest


def _is_option(arg):
    """Проверить, является ли аргумент ключом."""
    return arg.startswith(OPTION_PREFIX) and arg != OPTION_PREFIX


def require_dir(name, node):
    """Убедиться, что ``node`` — каталог.

    :raises CommandError: если это файл.
    """
    if not node.is_dir:
        raise CommandError(f"{name}: {node.path}: это не каталог")
    return node
