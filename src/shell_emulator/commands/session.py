"""Команды управления сеансом: exit, vfs-info."""

from .base import CommandError

MAX_EXIT_ARGS = 1


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


def cmd_vfs_info(shell, args):
    """Служебная команда: показать сведения о загруженной VFS."""
    if args:
        raise CommandError("vfs-info: команда не принимает аргументов")
    dirs, files, total = shell.vfs.stats()
    return "\n".join([
        f"имя:       {shell.vfs.name}",
        f"источник:  {shell.vfs.source or '<в памяти>'}",
        f"каталогов: {dirs}",
        f"файлов:    {files}",
        f"байт:      {total}",
    ])
