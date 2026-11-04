"""Реализация встроенных команд эмулятора.

Каждая команда — функция вида ``command(shell, args) -> str``.
Она возвращает текст для вывода или возбуждает :class:`CommandError`.
"""

MAX_CD_ARGS = 1
MAX_EXIT_ARGS = 1


class CommandError(Exception):
    """Ошибка выполнения команды (неверные аргументы и т. п.)."""


def cmd_ls(shell, args):
    """Заглушка ``ls``: вывести имя команды и аргументы."""
    return _stub("ls", args)


def cmd_cd(shell, args):
    """Заглушка ``cd``: проверить число аргументов и вывести их."""
    if len(args) > MAX_CD_ARGS:
        raise CommandError("cd: слишком много аргументов")
    return _stub("cd", args)


def cmd_exit(shell, args):
    """Завершить работу эмулятора с необязательным кодом возврата."""
    if len(args) > MAX_EXIT_ARGS:
        raise CommandError("exit: слишком много аргументов")
    code = 0
    if args:
        try:
            code = int(args[0])
        except ValueError as error:
            raise CommandError(
                f"exit: {args[0]}: требуется числовой аргумент"
            ) from error
    shell.stop(code)
    return ""


def _stub(name, args):
    """Сформировать вывод команды-заглушки."""
    return f"{name}: args={args!r}"


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
}
