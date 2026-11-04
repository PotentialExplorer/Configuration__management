"""Ядро эмулятора: выполнение команд, не зависящее от интерфейса."""

from dataclasses import dataclass

from .commands import COMMANDS, CommandError
from .parser import ParseError, parse_line

DEFAULT_VFS_NAME = "default"


@dataclass
class CommandResult:
    """Результат выполнения одной строки.

    :ivar output: текст, который нужно показать пользователю.
    :ivar error: ``True``, если при выполнении произошла ошибка.
    """

    output: str
    error: bool = False


class Shell:
    """Состояние сеанса эмулятора и диспетчер команд."""

    def __init__(self, vfs_name=DEFAULT_VFS_NAME):
        """Создать сеанс.

        :param vfs_name: имя VFS, отображаемое в заголовке окна.
        """
        self.vfs_name = vfs_name
        self.running = True
        self.exit_code = 0

    def prompt(self):
        """Вернуть строку приглашения к вводу."""
        return f"{self.vfs_name}:~$ "

    def stop(self, code=0):
        """Пометить сеанс завершённым с кодом ``code``."""
        self.running = False
        self.exit_code = code

    def execute(self, line):
        """Разобрать и выполнить строку команды.

        :param line: строка, введённая пользователем.
        :return: :class:`CommandResult` с выводом команды.
        """
        try:
            name, args = parse_line(line)
        except ParseError as error:
            return CommandResult(str(error), error=True)
        if name is None:
            return CommandResult("")
        handler = COMMANDS.get(name)
        if handler is None:
            return CommandResult(f"{name}: команда не найдена", error=True)
        try:
            return CommandResult(handler(self, args))
        except CommandError as error:
            return CommandResult(str(error), error=True)
