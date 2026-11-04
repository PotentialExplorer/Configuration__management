"""Ядро эмулятора: выполнение команд, не зависящее от интерфейса."""

from dataclasses import dataclass
from datetime import datetime

from .commands import COMMANDS, CommandError
from .parser import ParseError, parse_line
from .vfs import VfsError, create_default_vfs

USER = "user"
HOME_SIGN = "~"
HOME_PREFIX = "~/"


@dataclass
class CommandResult:
    """Результат выполнения одной строки.

    :ivar output: текст, который нужно показать пользователю.
    :ivar error: ``True``, если при выполнении произошла ошибка.
    :ivar stop: ``True``, если после команды сеанс завершён.
    """

    output: str
    error: bool = False
    stop: bool = False


class Shell:
    """Состояние сеанса эмулятора и диспетчер команд."""

    def __init__(self, vfs=None):
        """Создать сеанс над ``vfs`` (по умолчанию — VFS в памяти)."""
        self.vfs = vfs if vfs is not None else create_default_vfs()
        self.cwd = self.vfs.root
        self.user = USER
        self.clock = datetime.now
        self.running = True
        self.exit_code = 0

    @property
    def vfs_name(self):
        """Имя текущей VFS."""
        return self.vfs.name

    def prompt(self):
        """Вернуть строку приглашения к вводу."""
        return f"{self.user}@{self.vfs_name}:{self.cwd.path}$ "

    def stop(self, code=0):
        """Пометить сеанс завершённым с кодом ``code``."""
        self.running = False
        self.exit_code = code

    @property
    def home(self):
        """Домашний каталог: ``/home/<user>``, если он есть, иначе ``/``."""
        try:
            return self.vfs.resolve(f"/home/{self.user}")
        except VfsError:
            return self.vfs.root

    def expand_home(self, path):
        """Заменить ведущую ``~`` на путь домашнего каталога."""
        if path == HOME_SIGN or path.startswith(HOME_PREFIX):
            return self.home.path.rstrip("/") + "/" + path[1:].lstrip("/")
        return path

    def resolve(self, path):
        """Найти узел VFS относительно текущего каталога.

        :raises CommandError: если путь не существует.
        """
        try:
            return self.vfs.resolve(self.expand_home(path), self.cwd)
        except VfsError as error:
            raise CommandError(str(error)) from error

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
            output = handler(self, args)
            return CommandResult(output, stop=not self.running)
        except CommandError as error:
            return CommandResult(_with_prefix(name, error), error=True)


def _with_prefix(name, error):
    """Добавить имя команды в начало сообщения, если его там нет."""
    message = str(error)
    prefix = f"{name}: "
    return message if message.startswith(prefix) else prefix + message
